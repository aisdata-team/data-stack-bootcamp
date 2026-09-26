#!/usr/bin/env python3
"""Score one diagnostic response and place the learner, skill by skill.

This is the REFERENCE placement rule: the app (sub-project 2) must produce the
same placement for the same responses, and its tests should be written against
this function's behaviour.

    python3 scripts/score.py responses/<pseudonym>-<stage>-<form>.yaml

Responses file (gitignored — never committed):

    stage: 1
    form: A                 # A | B | screener (screener: stage 0 only)
    confidence:
      P1: [4, 5]            # one value 1–5 per statement, in the order shown
    answers:
      P1-A-01: B            # the letter shown on the paper form
      P1-A-02: "?"          # "?" or idk = I don't know
      P1-A-03: CADB         # ordering items: the letters in the learner's order

An item with no answer counts as "I don't know".
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from bank import (
    CONTENT_DIR,
    IDK_LABEL,
    ContentError,
    correct_answer,
    display_options,
    display_steps,
    load_questions,
    load_skills,
    load_yaml,
)

CONFIDENT_MEAN = 4.0  # "Agree" on the 5-point scale
PASS_FRACTION = (2, 3)  # at least 2 of 3; 1 of 1 on the screener
FIRST_STAGE_WITH_REQUIRED_LABS = 2  # stages 2–3: the diagnostic can skip readings only
IDK_ANSWERS = {IDK_LABEL, "idk", ""}


@dataclass
class SkillResult:
    skill: str
    stage: int
    confidence_mean: float | None
    correct: int
    wrong: int
    idk: int
    placement: str
    reading_required: bool
    lab_required: bool
    misconceptions: list[dict] = field(default_factory=list)


def select_items(bank: dict, skill: str, form: str) -> list[dict]:
    items = [i for i in bank[skill]["items"] if i.get("pool") == ("A" if form == "screener" else form)]
    items.sort(key=lambda i: i["id"])
    return items[:1] if form == "screener" else items


def grade(item: dict, answer) -> str:
    """Return 'correct', 'wrong' or 'idk'."""
    given = "" if answer is None else str(answer).strip().upper()
    if given.lower() in IDK_ANSWERS or given == IDK_LABEL:
        return "idk"
    if item.get("type") == "ordering":
        letters = {letter for letter, _ in display_steps(item)}
        if sorted(given) != sorted(letters):
            raise ValueError(
                f"{item['id']}: ordering answer `{given}` must use each of {''.join(sorted(letters))} once"
            )
    else:
        letters = {letter for letter, _ in display_options(item)}
        if given not in letters:
            raise ValueError(f"{item['id']}: answer `{given}` is not one of {''.join(sorted(letters))} or {IDK_LABEL}")
    return "correct" if given == correct_answer(item) else "wrong"


def misconception(item: dict, given: str) -> dict:
    if item.get("type") == "ordering":
        return {
            "item": item["id"],
            "chosen": given,
            "correct": correct_answer(item),
            "why": " → ".join(step["rationale"] for step in item["steps"]),
        }
    chosen = dict(display_options(item))[given]
    return {"item": item["id"], "chosen": chosen["text"], "correct": correct_answer(item), "why": chosen["rationale"]}


def place(confident: bool, passed: bool, wrong: int) -> str:
    if passed:
        return "place_out" if confident else "prove_it"
    return "take_flagged" if confident and wrong > 0 else "take"


def score(bank: dict, skills: dict[str, dict], responses: dict) -> list[SkillResult]:
    form = str(responses.get("form", ""))
    stage = responses.get("stage")
    if form not in {"A", "B", "screener"}:
        raise ValueError("form must be A, B or screener")
    if form == "screener" and stage != 0:
        raise ValueError("the screener is a stage-0 form")
    in_scope = [sid for sid, s in skills.items() if s.get("stage") == stage and s.get("diagnostic") and sid in bank]
    if not in_scope:
        raise ValueError(f"no diagnostic skills with a question bank in stage {stage}")

    answers = responses.get("answers") or {}
    known = {i["id"] for sid in in_scope for i in select_items(bank, sid, form)}
    unknown = sorted(set(answers) - known)
    if unknown:
        raise ValueError(f"answers name items not on this form: {', '.join(unknown)}")
    confidence = responses.get("confidence") or {}
    unknown = sorted(set(confidence) - set(in_scope))
    if unknown:
        raise ValueError(f"confidence names skills not on this form: {', '.join(unknown)}")

    results = []
    for sid in in_scope:
        values = confidence.get(sid) or []
        if any(not isinstance(v, int) or not 1 <= v <= 5 for v in values):
            raise ValueError(f"{sid}: confidence values must be integers 1–5")
        mean = sum(values) / len(values) if values else None
        tally = {"correct": 0, "wrong": 0, "idk": 0}
        wrongs = []
        items = select_items(bank, sid, form)
        for item in items:
            outcome = grade(item, answers.get(item["id"]))
            tally[outcome] += 1
            if outcome == "wrong":
                wrongs.append(misconception(item, str(answers[item["id"]]).strip().upper()))
        confident = mean is not None and mean >= CONFIDENT_MEAN
        num, den = PASS_FRACTION
        passed = tally["correct"] * den >= num * len(items)
        placement = place(confident, passed, tally["wrong"])
        skill_stage = skills[sid]["stage"]
        labs_always = skill_stage >= FIRST_STAGE_WITH_REQUIRED_LABS
        results.append(
            SkillResult(
                skill=sid,
                stage=skill_stage,
                confidence_mean=mean,
                correct=tally["correct"],
                wrong=tally["wrong"],
                idk=tally["idk"],
                placement=placement,
                reading_required=placement in {"take", "take_flagged"},
                lab_required=labs_always or placement != "place_out",
                misconceptions=wrongs if placement == "take_flagged" else [],
            )
        )
    return results


def load_bank(content_dir: Path) -> dict:
    return {
        qf.skill: {"confidence": qf.data.get("confidence"), "items": qf.items} for qf in load_questions(content_dir)
    }


def render(results: list[SkillResult]) -> str:
    lines = [
        "| Skill | Confidence | Correct | Wrong | Don't know | Placement | Reading | Lab |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        conf = "—" if r.confidence_mean is None else f"{r.confidence_mean:.1f}"
        lines.append(
            f"| {r.skill} | {conf} | {r.correct} | {r.wrong} | {r.idk} | {r.placement} | "
            f"{'required' if r.reading_required else 'optional'} | {'required' if r.lab_required else 'optional'} |"
        )
    flagged = [r for r in results if r.misconceptions]
    if flagged:
        lines += ["", "**Misconceptions** (confident, and a wrong answer chosen):"]
        for r in flagged:
            for m in r.misconceptions:
                lines.append(f"- {m['item']}: chose “{m['chosen']}” (correct: {m['correct']}) — {m['why']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Score one diagnostic response.")
    parser.add_argument("responses", type=Path)
    parser.add_argument("--content", type=Path, default=CONTENT_DIR)
    args = parser.parse_args(argv)
    try:
        skills = {s["id"]: s for s in load_skills(args.content)}
        results = score(load_bank(args.content), skills, load_yaml(args.responses) or {})
    except (ContentError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(render(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
