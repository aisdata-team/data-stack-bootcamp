import pytest
from conftest import ROOT, edit_front_matter, edit_yaml
from validate_content import validate


def errors_for(content):
    return validate(content)[0]


def test_template_tree_passes(content):
    assert errors_for(content) == []


def test_the_real_content_passes():
    errors, report = validate(ROOT / "content")
    assert errors == []
    assert report  # the coverage report always prints


def test_empty_content_dir_fails(tmp_path):
    assert errors_for(tmp_path)  # no skills.yaml at all


def test_no_skills_fails(content):
    (content / "skills.yaml").write_text("skills: []\n")
    assert any("empty course" in e for e in errors_for(content))


# --- skills.yaml -------------------------------------------------------------


def test_duplicate_skill_id(content):
    edit_yaml(content / "skills.yaml", lambda d: d["skills"].append(dict(d["skills"][0])))
    assert any("duplicate id" in e for e in errors_for(content))


def test_unknown_prerequisite(content):
    edit_yaml(content / "skills.yaml", lambda d: d["skills"][1].update(prerequisites=["Z9"]))
    assert any("prerequisite `Z9`" in e for e in errors_for(content))


def test_prerequisite_in_later_stage(content):
    edit_yaml(content / "skills.yaml", lambda d: d["skills"][0].update(prerequisites=["P1"]))
    assert any("later stage" in e for e in errors_for(content))


# --- units -------------------------------------------------------------------

UNIT = "units/F1-01-example/unit.md"


def test_unit_missing_front_matter_field(content):
    edit_front_matter(content / UNIT, lambda m: m.pop("minutes"))
    assert any("front-matter missing minutes" in e for e in errors_for(content))


def test_unit_bad_sha(content):
    edit_front_matter(content / UNIT, lambda m: m["sources"][0].update(commit="abc123"))
    assert any("not a full 40-hex SHA" in e for e in errors_for(content))


def test_unit_empty_sources(content):
    edit_front_matter(content / UNIT, lambda m: m.update(sources=[]))
    assert any("`sources` is empty" in e for e in errors_for(content))


def test_unit_folder_must_match_id(content):
    (content / "units" / "F1-01-example").rename(content / "units" / "F1-02-example")
    assert any("folder name must be" in e for e in errors_for(content))


def test_unit_stage_must_match_skill(content):
    edit_front_matter(content / UNIT, lambda m: m.update(stage=1))
    assert any("stage does not match" in e for e in errors_for(content))


def test_unit_unknown_skill(content):
    edit_front_matter(content / UNIT, lambda m: m.update(skill="Z9"))
    assert any("skill `Z9` is not in skills.yaml" in e for e in errors_for(content))


def test_unit_missing_reading_section(content):
    path = content / UNIT
    path.write_text(path.read_text().replace("## Ask the tutor", "## Something else"))
    assert any("missing section `## Ask the tutor`" in e for e in errors_for(content))


def test_unit_missing_lab(content):
    (content / "units" / "F1-01-example" / "lab.md").unlink()
    assert any("missing lab.md" in e for e in errors_for(content))


def test_lab_missing_section(content):
    path = content / "units" / "F1-01-example" / "lab.md"
    path.write_text(path.read_text().replace("## Reset", "## Cleanup"))
    assert any("lab.md: missing section `## Reset`" in e for e in errors_for(content))


# --- questions ---------------------------------------------------------------

Q = "questions/F1.yaml"


def items_where(pred):
    def fn(d):
        d["items"] = [i for i in d["items"] if not pred(i)]

    return fn


def test_pool_needs_three_items(content):
    edit_yaml(content / Q, items_where(lambda i: i["id"] == "F1-A-03"))
    assert any("pool A needs exactly 3 items, has 2" in e for e in errors_for(content))


def test_confidence_needs_two_statements(content):
    edit_yaml(content / Q, lambda d: d["confidence"]["B"].pop())
    assert any("confidence.B needs exactly 2" in e for e in errors_for(content))


def test_exactly_one_correct_option(content):
    edit_yaml(content / Q, lambda d: d["items"][0]["options"][1].update(correct=True))
    assert any("exactly one correct option, has 2" in e for e in errors_for(content))


def test_every_option_needs_a_rationale(content):
    edit_yaml(content / Q, lambda d: d["items"][0]["options"][1].update(rationale=""))
    assert any("options[1] needs a rationale" in e for e in errors_for(content))


@pytest.mark.parametrize("text", ["I don't know", "I don’t know", "Not sure", "IDK"])
def test_authored_idk_option_fails(content, text):
    edit_yaml(
        content / Q, lambda d: d["items"][0]["options"].append({"text": text, "correct": False, "rationale": "x"})
    )
    assert any("never author it" in e for e in errors_for(content))


def test_artifact_item_needs_artifact(content):
    edit_yaml(content / Q, lambda d: d["items"][1].update(artifact=None))
    assert any("needs an `artifact`" in e for e in errors_for(content))


def test_ordering_needs_three_steps(content):
    edit_yaml(content / Q, lambda d: d["items"][2].update(steps=d["items"][2]["steps"][:2]))
    assert any("at least 3 steps" in e for e in errors_for(content))


def test_unit_pool_item_names_existing_unit(content):
    edit_yaml(content / Q, lambda d: d["items"][-1].update(unit="F1-09"))
    assert any("unit `F1-09` does not exist" in e for e in errors_for(content))


def test_duplicate_item_id(content):
    edit_yaml(content / Q, lambda d: d["items"][4].update(id="F1-B-01"))
    assert any("duplicate item id" in e for e in errors_for(content))


def test_item_id_must_match_skill_and_pool(content):
    edit_yaml(content / Q, lambda d: d["items"][0].update(id="F1-B-09"))
    assert any("id must look like F1-A-01" in e for e in errors_for(content))


def test_file_name_must_match_skill(content):
    (content / Q).rename(content / "questions" / "P1.yaml")
    assert any("must match the file name" in e for e in errors_for(content))


def test_later_stage_items_must_cite_sources(content):
    def to_p1(d):
        d["skill"] = "P1"
        for item in d["items"]:
            item["id"] = item["id"].replace("F1-", "P1-")
            item["unit"] = None if item["pool"] != "unit" else item["unit"]
        d["items"] = [i for i in d["items"] if i["pool"] != "unit"]

    edit_yaml(content / Q, to_p1)
    (content / Q).rename(content / "questions" / "P1.yaml")
    assert any("`sources` is empty" in e for e in errors_for(content))


def test_long_key_is_flagged_but_not_an_error(content):
    def lengthen(d):
        d["items"][0]["options"][0]["text"] = "WHERE, which filters the rows before any grouping or ordering happens"

    edit_yaml(content / Q, lengthen)
    errors, report = validate(content)
    assert errors == []
    assert any("advisory" in line and "F1-A-01" in line for line in report)
