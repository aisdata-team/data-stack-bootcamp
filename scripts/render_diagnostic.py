#!/usr/bin/env python3
"""Print a stage diagnostic as markdown, for the weekly hour before the app exists.

    python3 scripts/render_diagnostic.py --stage 1 --form A          > stage1-A.md
    python3 scripts/render_diagnostic.py --stage 1 --form A --key    > stage1-A-key.md
    python3 scripts/render_diagnostic.py --stage 0 --screener        > screener.md

The learner's form never contains an answer. Every item ends with the
"I don't know" choice (`?`), because without it a guess counts as knowledge.
Letters come from `bank.display_options` / `display_steps`, the same order the
scorer reads back, so a letter written on paper scores exactly as shown.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bank import (
    CONTENT_DIR,
    IDK_LABEL,
    IDK_TEXT,
    ContentError,
    correct_answer,
    display_options,
    display_steps,
    load_questions,
    load_skills,
)
from score import select_items

SCALE = "1 strongly disagree · 2 disagree · 3 neither · 4 agree · 5 strongly agree"


def skills_in_scope(content_dir: Path, stage: int) -> list[tuple[dict, dict]]:
    """[(skill, question file data)] for the stage's diagnostic skills that have a bank, in skills.yaml order."""
    banks = {qf.skill: qf for qf in load_questions(content_dir)}
    scoped = [
        (s, {"confidence": banks[s["id"]].data.get("confidence"), "items": banks[s["id"]].items})
        for s in load_skills(content_dir)
        if s.get("stage") == stage and s.get("diagnostic") and s["id"] in banks
    ]
    if not scoped:
        raise ContentError(f"no diagnostic skills with a question bank in stage {stage}")
    return scoped


def render_item(item: dict, key: bool) -> list[str]:
    out = [f"**{item['id']}.** {item['stem'].strip()}", ""]
    if item.get("artifact"):
        out += ["```", item["artifact"].rstrip("\n"), "```", ""]
    if item.get("type") == "ordering":
        out.append("Write the letters in the correct order:")
        out += [f"- **{letter}** {step['text']}" for letter, step in display_steps(item)]
    else:
        out += [f"- **{letter}** {option['text']}" for letter, option in display_options(item)]
    out.append(f"- **{IDK_LABEL}** {IDK_TEXT}")
    out.append("")
    if key:
        out.append(f"> **Answer: {correct_answer(item)}**")
        if item.get("type") == "ordering":
            for step in item["steps"]:
                out.append(f"> - {step['text']}: {step['rationale']}")
        else:
            for letter, option in display_options(item):
                mark = "✓" if option.get("correct") else "✗"
                out.append(f"> - {letter} {mark} {option['rationale']}")
        out.append("")
    else:
        out += ["Answer: ______", ""]
    return out


def render(content_dir: Path, stage: int, form: str, key: bool) -> str:
    scoped = skills_in_scope(content_dir, stage)
    confidence_form = "A" if form == "screener" else form
    title = "Stage 0 screener" if form == "screener" else f"Stage {stage} diagnostic — form {form}"
    lines = [f"# {title}{' — ANSWER KEY' if key else ''}", ""]
    if not key:
        lines += [
            "This places you in the course, skill by skill. It is **never** used for performance evaluation.",
            "",
            f"If you don't know an answer, choose **{IDK_LABEL}** — a guess tells us less than an honest "
            '"I don\'t know".',
            "",
            "Pseudonym: ____________  Date: ____________",
            "",
        ]
    for skill, bank in scoped:
        lines += [f"## {skill['id']} · {skill['title']}", ""]
        if not key:
            lines += [f"Rate each statement ({SCALE}):", ""]
            for statement in (bank.get("confidence") or {}).get(confidence_form) or []:
                lines.append(f"- {statement}  **[   ]**")
            lines.append("")
        for item in select_items({skill["id"]: bank}, skill["id"], form):
            lines += render_item(item, key)
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print a stage diagnostic as markdown.")
    parser.add_argument("--stage", type=int, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--form", choices=["A", "B"])
    group.add_argument("--screener", action="store_true", help="stage 0 only: one form-A item per skill")
    parser.add_argument("--key", action="store_true", help="print the answer key instead of the learner's form")
    parser.add_argument("--content", type=Path, default=CONTENT_DIR)
    args = parser.parse_args(argv)
    if args.screener and args.stage != 0:
        parser.error("the screener is a stage-0 form")
    try:
        print(render(args.content, args.stage, "screener" if args.screener else args.form, args.key), end="")
    except ContentError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
