import pytest
from bank import correct_answer, display_options, display_steps
from score import score


def mcq(iid):
    return {
        "id": iid,
        "pool": iid.split("-")[1],
        "type": "mcq",
        "stem": "q",
        "options": [
            {"text": "right", "correct": True, "rationale": "because"},
            {"text": "wrong", "correct": False, "rationale": "the misconception"},
            {"text": "also wrong", "correct": False, "rationale": "another"},
        ],
    }


def ordering(iid):
    return {
        "id": iid,
        "pool": iid.split("-")[1],
        "type": "ordering",
        "stem": "q",
        "steps": [{"text": f"s{i}", "rationale": f"r{i}"} for i in range(4)],
    }


def wrong_letter(item):
    return next(letter for letter, o in display_options(item) if not o["correct"])


SKILLS = {
    "F1": {"id": "F1", "stage": 0, "diagnostic": True},
    "P1": {"id": "P1", "stage": 1, "diagnostic": True},
    "O1": {"id": "O1", "stage": 2, "diagnostic": True},
}
BANK = {
    sid: {
        "items": [
            mcq(f"{sid}-A-01"),
            mcq(f"{sid}-A-02"),
            ordering(f"{sid}-A-03"),
            mcq(f"{sid}-B-01"),
            mcq(f"{sid}-B-02"),
            mcq(f"{sid}-B-03"),
        ]
    }
    for sid in SKILLS
}


def items(sid, form="A"):
    return [i for i in BANK[sid]["items"] if i["pool"] == form]


def run(stage, sid, confidence, answers, form="A"):
    responses = {"stage": stage, "form": form, "confidence": {sid: confidence}, "answers": answers}
    [result] = [r for r in score(BANK, SKILLS, responses) if r.skill == sid]
    return result


def all_correct(sid, form="A"):
    return {i["id"]: correct_answer(i) for i in items(sid, form)}


def test_confident_and_passed_places_out():
    r = run(1, "P1", [4, 5], all_correct("P1"))
    assert (r.placement, r.reading_required, r.lab_required) == ("place_out", False, False)


def test_not_confident_but_passed_proves_it_with_the_lab():
    r = run(1, "P1", [2, 3], all_correct("P1"))
    assert (r.placement, r.reading_required, r.lab_required) == ("prove_it", False, True)


def test_confident_and_wrong_is_flagged_with_the_misconception():
    a1, a2, a3 = items("P1")
    answers = {a1["id"]: wrong_letter(a1), a2["id"]: wrong_letter(a2), a3["id"]: correct_answer(a3)}
    r = run(1, "P1", [5, 5], answers)
    assert r.placement == "take_flagged"
    assert (r.correct, r.wrong, r.idk) == (1, 2, 0)
    assert {m["item"] for m in r.misconceptions} == {a1["id"], a2["id"]}
    assert all(m["why"] in {"the misconception", "another"} for m in r.misconceptions)


def test_not_confident_and_not_passed_takes_it():
    r = run(1, "P1", [1, 2], {})
    assert (r.placement, r.reading_required, r.lab_required) == ("take", True, True)


def test_confident_idk_is_not_a_misconception():
    r = run(1, "P1", [5, 5], {i["id"]: "?" for i in items("P1")})
    assert r.placement == "take"
    assert (r.idk, r.wrong, r.misconceptions) == (3, 0, [])


def test_unanswered_counts_as_idk():
    r = run(1, "P1", [3, 3], {})
    assert r.idk == 3


def test_stage_two_never_waives_the_lab():
    r = run(2, "O1", [5, 5], all_correct("O1"))
    assert (r.placement, r.reading_required, r.lab_required) == ("place_out", False, True)


def test_wrong_ordering_is_wrong():
    a3 = items("P1")[2]
    right = correct_answer(a3)
    answers = {a3["id"]: right[::-1]}
    r = run(1, "P1", [3, 3], answers)
    assert r.wrong == 1


def test_ordering_must_use_every_letter_once():
    a3 = items("P1")[2]
    with pytest.raises(ValueError, match="each of"):
        run(1, "P1", [3, 3], {a3["id"]: "AAB"})


def test_unknown_item_is_an_error():
    with pytest.raises(ValueError, match="not on this form"):
        run(1, "P1", [3, 3], {"P1-A-99": "A"})


def test_item_from_the_other_form_is_an_error():
    with pytest.raises(ValueError, match="not on this form"):
        run(1, "P1", [3, 3], {"P1-B-01": "A"})


def test_letter_not_shown_is_an_error():
    with pytest.raises(ValueError, match="is not one of"):
        run(1, "P1", [3, 3], {"P1-A-01": "Z"})


def test_confidence_out_of_range_is_an_error():
    with pytest.raises(ValueError, match="1–5"):
        run(1, "P1", [6, 3], {})


def test_screener_uses_one_item_and_one_right_answer_passes():
    first = items("F1")[0]
    r = run(0, "F1", [2, 2], {first["id"]: correct_answer(first)}, form="screener")
    assert (r.correct, r.placement) == (1, "prove_it")


def test_screener_is_stage_zero_only():
    with pytest.raises(ValueError, match="stage-0"):
        run(1, "P1", [3, 3], {}, form="screener")


def test_display_letters_are_what_is_scored():
    # The scorer reads letters through the same display order the renderer prints.
    a3 = items("P1")[2]
    assert len(display_steps(a3)) == 4
