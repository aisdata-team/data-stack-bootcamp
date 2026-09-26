import re

import pytest
import yaml
from bank import IDK_LABEL, IDK_TEXT, ContentError, correct_answer, load_questions
from conftest import edit_yaml
from render_diagnostic import render


def item_blocks(markdown: str) -> list[str]:
    """Split a rendered form into one block per item (from its bold id to the next)."""
    return re.split(r"\n(?=\*\*[A-Z][0-9]+-[ABU]-[0-9]+\.\*\*)", markdown)[1:]


def test_every_item_offers_i_dont_know(content):
    blocks = item_blocks(render(content, 0, "A", key=False))
    assert len(blocks) == 3
    assert all(f"**{IDK_LABEL}** {IDK_TEXT}" in b for b in blocks)


def test_learner_form_carries_no_answers_or_rationales(content):
    out = render(content, 0, "A", key=False)
    [bank] = load_questions(content)
    assert "Answer: ______" in out and "ANSWER KEY" not in out
    for item in bank.items:
        for option in item.get("options") or []:
            assert option["rationale"] not in out
        for step in item.get("steps") or []:
            assert step["rationale"] not in out


def test_key_gives_the_scored_letter(content):
    out = render(content, 0, "A", key=True)
    [bank] = load_questions(content)
    for item in (i for i in bank.items if i["pool"] == "A"):
        assert f"**Answer: {correct_answer(item)}**" in out


def test_form_b_uses_form_b_items_and_statements(content):
    out = render(content, 0, "B", key=False)
    data = yaml.safe_load((content / "questions" / "F1.yaml").read_text())
    assert all(s in out for s in data["confidence"]["B"])
    assert "F1-A-01" not in out and "F1-B-01" in out


def test_screener_has_one_item_per_stage_zero_skill(content):
    blocks = item_blocks(render(content, 0, "screener", key=False))
    assert [b.split(".**")[0] for b in blocks] == ["**F1-A-01"]


def test_stage_with_no_bank_is_an_error(content):
    edit_yaml(content / "skills.yaml", lambda d: d["skills"].append({**d["skills"][1], "id": "P2"}))
    with pytest.raises(ContentError, match="stage 3"):
        render(content, 3, "A", key=False)
