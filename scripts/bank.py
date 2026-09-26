"""Shared loaders for the course content: the skills map, units and the question bank.

Every script (validate_content, score, check_source_drift, render_diagnostic) reads
content through here, so there is one definition of where things live and how an
item is displayed. `display_options` / `display_steps` are the ONLY place the
on-paper (and later in-app) order is decided: the scorer maps a learner's letter
back through the same function, so the two can never disagree.
"""

from __future__ import annotations

import hashlib
import string
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
TEMPLATES_DIRNAME = "_templates"
IDK_LABEL = "?"
IDK_TEXT = "I don't know"
LETTERS = string.ascii_uppercase


class ContentError(Exception):
    """Raised when content cannot be loaded at all (missing file, unparsable YAML)."""


@dataclass
class Unit:
    folder: Path
    meta: dict
    body: str
    lab: str | None

    @property
    def id(self) -> str:
        return str(self.meta.get("id", ""))


@dataclass
class QuestionFile:
    path: Path
    data: dict
    items: list[dict] = field(default_factory=list)

    @property
    def skill(self) -> str:
        return str(self.data.get("skill", ""))


def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ContentError(f"{path}: file not found") from e
    except yaml.YAMLError as e:
        raise ContentError(f"{path}: invalid YAML: {e}") from e


def split_front_matter(text: str) -> tuple[dict | None, str]:
    """Return (front-matter dict, body). Front-matter is a leading `---` … `---` block."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    meta = yaml.safe_load(text[4:end]) or {}
    return (meta if isinstance(meta, dict) else None), text[end + 5 :]


def load_skills(content_dir: Path = CONTENT_DIR) -> list[dict]:
    data = load_yaml(content_dir / "skills.yaml")
    if not isinstance(data, dict) or not isinstance(data.get("skills"), list):
        raise ContentError(f"{content_dir / 'skills.yaml'}: expected a top-level `skills:` list")
    return data["skills"]


def load_units(content_dir: Path = CONTENT_DIR) -> list[Unit]:
    units_dir = content_dir / "units"
    if not units_dir.is_dir():
        return []
    units = []
    for folder in sorted(p for p in units_dir.iterdir() if p.is_dir()):
        unit_md = folder / "unit.md"
        if not unit_md.is_file():
            units.append(Unit(folder, {}, "", None))
            continue
        try:
            meta, body = split_front_matter(unit_md.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            raise ContentError(f"{unit_md}: invalid front-matter YAML: {e}") from e
        lab_md = folder / "lab.md"
        lab = lab_md.read_text(encoding="utf-8") if lab_md.is_file() else None
        units.append(Unit(folder, meta or {}, body, lab))
    return units


def load_questions(content_dir: Path = CONTENT_DIR) -> list[QuestionFile]:
    qdir = content_dir / "questions"
    if not qdir.is_dir():
        return []
    files = []
    for path in sorted(qdir.glob("*.yaml")):
        data = load_yaml(path)
        if not isinstance(data, dict):
            raise ContentError(f"{path}: expected a mapping at the top level")
        items = data.get("items") or []
        files.append(QuestionFile(path, data, items if isinstance(items, list) else []))
    return files


def _seeded_order(item_id: str, n: int) -> list[int]:
    """A deterministic permutation of range(n), keyed on the item id.

    Authors tend to write the correct option first; displaying in authored order
    would leak the answer. Seeding on the id keeps the order stable across renders
    and between the renderer and the scorer.
    """
    return sorted(range(n), key=lambda i: hashlib.sha256(f"{item_id}:{i}".encode()).hexdigest())


def display_options(item: dict) -> list[tuple[str, dict]]:
    """[(letter, option), …] in display order for an mcq/artifact item. IDK is not included."""
    options = item.get("options") or []
    order = _seeded_order(str(item.get("id")), len(options))
    return [(LETTERS[pos], options[i]) for pos, i in enumerate(order)]


def display_steps(item: dict) -> list[tuple[str, dict]]:
    """[(letter, step), …] in shuffled display order for an ordering item."""
    steps = item.get("steps") or []
    order = _seeded_order(str(item.get("id")), len(steps))
    return [(LETTERS[pos], steps[i]) for pos, i in enumerate(order)]


def correct_answer(item: dict) -> str:
    """The correct answer as the learner would write it: one letter, or a letter sequence."""
    if item.get("type") == "ordering":
        shown = display_steps(item)
        by_step = {id(step): letter for letter, step in shown}
        return "".join(by_step[id(step)] for step in item.get("steps") or [])
    for letter, option in display_options(item):
        if option.get("correct") is True:
            return letter
    raise ContentError(f"item {item.get('id')}: no correct option")
