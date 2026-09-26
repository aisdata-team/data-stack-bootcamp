#!/usr/bin/env python3
"""Validate the course content: the skills map, every unit and the question bank.

Fails (exit 1) on any structural error, naming the file and field. Prints a
coverage report that never fails: which diagnostic skills still have no
questions file, and which have no units yet.

A tree with no skills FAILS — a validator that passes on nothing is the fail-open
shape the orchestration repo's CLAUDE.md rules out.

    python3 scripts/validate_content.py [--content content]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from bank import (
    CONTENT_DIR,
    TEMPLATES_DIRNAME,
    ContentError,
    load_questions,
    load_skills,
    load_units,
)

AUDIENCES = {"all", "data", "it"}
ITEM_TYPES = {"mcq", "artifact", "ordering"}
POOLS = {"A", "B", "unit"}
POOL_CODE = {"A": "A", "B": "B", "unit": "U"}
FORMS = ("A", "B")
CONFIDENCE_PER_FORM = 2
ITEMS_PER_FORM = 3
GIVEAWAY_RATIO = 1.5  # a key this much longer than every distractor reads as the answer
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SKILL_ID_RE = re.compile(r"^[A-Z][0-9]+$")
UNIT_ID_RE = re.compile(r"^([A-Z][0-9]+)-[0-9]{2}$")
IDK_LIKE = {
    "i dont know",
    "i do not know",
    "dont know",
    "do not know",
    "not sure",
    "unsure",
    "idk",
    "no idea",
}

UNIT_FIELDS = ("id", "skill", "stage", "title", "minutes", "prerequisites", "audience", "skippable", "sources")
READING_SECTIONS = (
    "Why this matters here",
    "The concept",
    "How it looks in our stack",
    "Lab",
    "Check questions",
    "Ask the tutor",
)
LAB_SECTIONS = (
    "Goal",
    "Environment",
    "Steps",
    "You're done when",
    "Evidence",
    "Common mistakes",
    "Reset",
    "Stretch",
)


def headings(markdown: str) -> set[str]:
    return {line[3:].strip() for line in markdown.splitlines() if line.startswith("## ")}


def check_sources(sources, where: str, errors: list[str], *, allow_empty: bool) -> None:
    if not isinstance(sources, list):
        errors.append(f"{where}: `sources` must be a list")
        return
    if not sources and not allow_empty:
        errors.append(f"{where}: `sources` is empty — every claim about the stack cites a file")
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            errors.append(f"{where}: sources[{i}] must be a mapping of repo/path/commit")
            continue
        for key in ("repo", "path", "commit"):
            if not str(src.get(key) or "").strip():
                errors.append(f"{where}: sources[{i}] is missing `{key}`")
        commit = str(src.get("commit") or "")
        if commit and not SHA_RE.match(commit):
            errors.append(f"{where}: sources[{i}].commit `{commit}` is not a full 40-hex SHA")


def validate_skills(skills: list[dict], errors: list[str]) -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    for i, skill in enumerate(skills):
        where = f"skills.yaml: skills[{i}]"
        if not isinstance(skill, dict):
            errors.append(f"{where}: must be a mapping")
            continue
        sid = str(skill.get("id") or "")
        if not SKILL_ID_RE.match(sid):
            errors.append(f"{where}: id `{sid}` must look like F1 / P6 / C7")
            continue
        where = f"skills.yaml: {sid}"
        if sid in by_id:
            errors.append(f"{where}: duplicate id")
        by_id[sid] = skill
        if skill.get("stage") not in range(5):
            errors.append(f"{where}: stage must be 0–4")
        if not str(skill.get("title") or "").strip():
            errors.append(f"{where}: missing title")
        if not isinstance(skill.get("units"), int) or skill["units"] < 0:
            errors.append(f"{where}: units must be a non-negative integer")
        if skill.get("audience") not in AUDIENCES:
            errors.append(f"{where}: audience must be one of {sorted(AUDIENCES)}")
        if not isinstance(skill.get("diagnostic"), bool):
            errors.append(f"{where}: diagnostic must be true or false")
        if not isinstance(skill.get("prerequisites"), list):
            errors.append(f"{where}: prerequisites must be a list")
    for sid, skill in by_id.items():
        for pre in skill.get("prerequisites") or []:
            if pre not in by_id:
                errors.append(f"skills.yaml: {sid}: prerequisite `{pre}` is not a skill")
            elif by_id[pre].get("stage", 0) > skill.get("stage", 0):
                errors.append(f"skills.yaml: {sid}: prerequisite `{pre}` is in a later stage")
    return by_id


def validate_units(units, skills: dict[str, dict], errors: list[str]) -> dict[str, object]:
    by_id: dict[str, object] = {}
    for unit in units:
        folder = unit.folder.name
        where = f"units/{folder}"
        if not (unit.folder / "unit.md").is_file():
            errors.append(f"{where}: missing unit.md")
            continue
        missing = [f for f in UNIT_FIELDS if f not in unit.meta]
        if missing:
            errors.append(f"{where}/unit.md: front-matter missing {', '.join(missing)}")
            continue
        uid = unit.id
        m = UNIT_ID_RE.match(uid)
        if not m:
            errors.append(f"{where}/unit.md: id `{uid}` must look like F3-01")
            continue
        if uid in by_id:
            errors.append(f"{where}/unit.md: duplicate unit id `{uid}`")
        by_id[uid] = unit
        if folder != uid and not folder.startswith(uid + "-"):
            errors.append(f"{where}: folder name must be `{uid}` or start with `{uid}-`")
        skill = unit.meta.get("skill")
        if skill not in skills:
            errors.append(f"{where}/unit.md: skill `{skill}` is not in skills.yaml")
        else:
            if m.group(1) != skill:
                errors.append(f"{where}/unit.md: id `{uid}` does not start with its skill `{skill}`")
            if unit.meta.get("stage") != skills[skill].get("stage"):
                errors.append(f"{where}/unit.md: stage does not match skill {skill}'s stage")
        if not isinstance(unit.meta.get("minutes"), int) or not 15 <= unit.meta["minutes"] <= 120:
            errors.append(f"{where}/unit.md: minutes must be an integer from 15 to 120")
        if unit.meta.get("audience") not in AUDIENCES:
            errors.append(f"{where}/unit.md: audience must be one of {sorted(AUDIENCES)}")
        if not isinstance(unit.meta.get("skippable"), bool):
            errors.append(f"{where}/unit.md: skippable must be true or false")
        if not isinstance(unit.meta.get("prerequisites"), list):
            errors.append(f"{where}/unit.md: prerequisites must be a list")
        check_sources(unit.meta.get("sources"), f"{where}/unit.md", errors, allow_empty=False)
        have = headings(unit.body)
        for section in READING_SECTIONS:
            if section not in have:
                errors.append(f"{where}/unit.md: missing section `## {section}`")
        if unit.lab is None:
            errors.append(f"{where}: missing lab.md")
        else:
            have = headings(unit.lab)
            for section in LAB_SECTIONS:
                if section not in have:
                    errors.append(f"{where}/lab.md: missing section `## {section}`")
    for uid, unit in by_id.items():
        for pre in unit.meta.get("prerequisites") or []:
            if pre not in by_id and pre not in skills:
                errors.append(f"units/{unit.folder.name}/unit.md: prerequisite `{pre}` is neither a unit nor a skill")
    return by_id


def normalise(text: str) -> str:
    return re.sub(r"[^a-z ]", "", text.lower().replace("’", "'").replace("'", "")).strip()


def validate_item(item: dict, qf, stage: int, units: dict, errors: list[str]) -> None:
    iid = str(item.get("id") or "")
    where = f"questions/{qf.path.name}: {iid or '<no id>'}"
    pool = item.get("pool")
    if pool not in POOLS:
        errors.append(f"{where}: pool must be A, B or unit")
        return
    expected_prefix = f"{qf.skill}-{POOL_CODE[pool]}-"
    if not iid.startswith(expected_prefix) or not iid[len(expected_prefix) :].isdigit():
        errors.append(f"{where}: id must look like {expected_prefix}01")
    if pool == "unit":
        if item.get("unit") not in units:
            errors.append(f"{where}: unit `{item.get('unit')}` does not exist")
    elif item.get("unit") is not None:
        errors.append(f"{where}: only unit-pool items name a unit")
    kind = item.get("type")
    if kind not in ITEM_TYPES:
        errors.append(f"{where}: type must be one of {sorted(ITEM_TYPES)}")
        return
    if not str(item.get("stem") or "").strip():
        errors.append(f"{where}: missing stem")
    if kind == "artifact" and not str(item.get("artifact") or "").strip():
        errors.append(f"{where}: an artifact item needs an `artifact`")
    if kind == "ordering":
        steps = item.get("steps")
        if not isinstance(steps, list) or len(steps) < 3:
            errors.append(f"{where}: an ordering item needs at least 3 steps")
        else:
            for i, step in enumerate(steps):
                if not isinstance(step, dict) or not str(step.get("text") or "").strip():
                    errors.append(f"{where}: steps[{i}] needs text")
                elif not str(step.get("rationale") or "").strip():
                    errors.append(f"{where}: steps[{i}] needs a rationale")
        if item.get("options"):
            errors.append(f"{where}: an ordering item has steps, not options")
    else:
        options = item.get("options")
        if not isinstance(options, list) or len(options) < 2:
            errors.append(f"{where}: needs at least 2 options")
        else:
            correct = [o for o in options if isinstance(o, dict) and o.get("correct") is True]
            if len(correct) != 1:
                errors.append(f"{where}: needs exactly one correct option, has {len(correct)}")
            for i, option in enumerate(options):
                if not isinstance(option, dict) or not str(option.get("text") or "").strip():
                    errors.append(f"{where}: options[{i}] needs text")
                    continue
                if not str(option.get("rationale") or "").strip():
                    errors.append(f"{where}: options[{i}] needs a rationale")
                if normalise(str(option["text"])) in IDK_LIKE:
                    errors.append(
                        f"{where}: options[{i}] is an 'I don't know' option — never author it, it is always added"
                    )
    check_sources(item.get("sources", None), where, errors, allow_empty=stage == 0)


def validate_questions(files, skills: dict[str, dict], units: dict, errors: list[str]) -> set[str]:
    covered: set[str] = set()
    seen_ids: set[str] = set()
    for qf in files:
        where = f"questions/{qf.path.name}"
        if qf.skill != qf.path.stem:
            errors.append(f"{where}: `skill: {qf.skill}` must match the file name")
            continue
        skill = skills.get(qf.skill)
        if skill is None:
            errors.append(f"{where}: skill `{qf.skill}` is not in skills.yaml")
            continue
        if not skill.get("diagnostic"):
            errors.append(f"{where}: skill {qf.skill} has diagnostic: false")
        covered.add(qf.skill)
        confidence = qf.data.get("confidence")
        if not isinstance(confidence, dict):
            errors.append(f"{where}: missing `confidence` with forms A and B")
        else:
            for form in FORMS:
                statements = confidence.get(form)
                if not isinstance(statements, list) or len(statements) != CONFIDENCE_PER_FORM:
                    errors.append(f"{where}: confidence.{form} needs exactly {CONFIDENCE_PER_FORM} statements")
                elif not all(str(s or "").strip() for s in statements):
                    errors.append(f"{where}: confidence.{form} has an empty statement")
        counts = {pool: 0 for pool in POOLS}
        for item in qf.items:
            if not isinstance(item, dict):
                errors.append(f"{where}: every item must be a mapping")
                continue
            iid = str(item.get("id") or "")
            if iid in seen_ids:
                errors.append(f"{where}: duplicate item id `{iid}`")
            seen_ids.add(iid)
            if item.get("pool") in counts:
                counts[item["pool"]] += 1
            validate_item(item, qf, skill.get("stage", 0), units, errors)
        for form in FORMS:
            if counts[form] != ITEMS_PER_FORM:
                errors.append(f"{where}: pool {form} needs exactly {ITEMS_PER_FORM} items, has {counts[form]}")
    return covered


def giveaways(files) -> list[str]:
    """Item ids whose correct option is conspicuously longer than every distractor (advisory)."""
    flagged = []
    for qf in files:
        for item in qf.items:
            if not isinstance(item, dict) or item.get("type") == "ordering":
                continue
            options = [o for o in item.get("options") or [] if isinstance(o, dict)]
            keys = [len(str(o.get("text", ""))) for o in options if o.get("correct") is True]
            others = [len(str(o.get("text", ""))) for o in options if o.get("correct") is not True]
            if len(keys) == 1 and others and keys[0] > GIVEAWAY_RATIO * max(others):
                flagged.append(str(item.get("id")))
    return flagged


def validate(content_dir: Path) -> tuple[list[str], list[str]]:
    """Return (errors, coverage report lines)."""
    errors: list[str] = []
    try:
        skills_list = load_skills(content_dir)
        units = [u for u in load_units(content_dir) if u.folder.name != TEMPLATES_DIRNAME]
        questions = load_questions(content_dir)
    except ContentError as e:
        return [str(e)], []
    if not skills_list:
        return ["skills.yaml: no skills — an empty course cannot pass"], []
    skills = validate_skills(skills_list, errors)
    unit_ids = validate_units(units, skills, errors)
    covered = validate_questions(questions, skills, unit_ids, errors)

    report = []
    diagnostic = [sid for sid, s in skills.items() if s.get("diagnostic")]
    missing_q = [sid for sid in diagnostic if sid not in covered]
    report.append(f"questions: {len(covered)} of {len(diagnostic)} diagnostic skills have a bank")
    if missing_q:
        report.append(f"  no bank yet: {' '.join(missing_q)}")
    with_units = {u.meta.get("skill") for u in unit_ids.values()}
    planned = [sid for sid, s in skills.items() if s.get("units")]
    report.append(
        f"units: {len(unit_ids)} written, covering {len(with_units & set(planned))} of {len(planned)} "
        "skills with planned units"
    )
    flagged = giveaways(questions)
    if flagged:
        report.append(f"advisory — key more than {GIVEAWAY_RATIO}x the longest distractor: {' '.join(flagged)}")
    return errors, report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--content", type=Path, default=CONTENT_DIR)
    args = parser.parse_args(argv)
    errors, report = validate(args.content)
    for line in report:
        print(line)
    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("content OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
