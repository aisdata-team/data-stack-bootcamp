"""Shared fixtures. The scripts import each other as top-level modules, so put scripts/ on the path."""

import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

TEMPLATES = ROOT / "content" / "_templates"


@pytest.fixture
def content(tmp_path: Path) -> Path:
    """A minimal valid content tree built FROM THE TEMPLATES, so the templates and the validator cannot drift apart."""
    root = tmp_path / "content"
    (root / "units" / "F1-01-example").mkdir(parents=True)
    (root / "questions").mkdir()
    skills = {
        "skills": [
            {
                "id": "F1",
                "stage": 0,
                "title": "SQL",
                "units": 1,
                "audience": "all",
                "prerequisites": [],
                "diagnostic": True,
            },
            {
                "id": "P1",
                "stage": 1,
                "title": "Stack",
                "units": 1,
                "audience": "all",
                "prerequisites": ["F1"],
                "diagnostic": True,
            },
        ]
    }
    (root / "skills.yaml").write_text(yaml.safe_dump(skills))
    shutil.copy(TEMPLATES / "unit.md", root / "units" / "F1-01-example" / "unit.md")
    shutil.copy(TEMPLATES / "lab.md", root / "units" / "F1-01-example" / "lab.md")
    shutil.copy(TEMPLATES / "questions.yaml", root / "questions" / "F1.yaml")
    return root


def edit_yaml(path: Path, fn) -> None:
    data = yaml.safe_load(path.read_text())
    fn(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def edit_front_matter(unit_md: Path, fn) -> None:
    text = unit_md.read_text()
    end = text.index("\n---\n", 4)
    meta = yaml.safe_load(text[4:end])
    fn(meta)
    unit_md.write_text("---\n" + yaml.safe_dump(meta, sort_keys=False) + text[end + 1 :])
