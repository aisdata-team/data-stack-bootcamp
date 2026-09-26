from bank import correct_answer, display_options, display_steps

MCQ = {
    "id": "X1-A-01",
    "type": "mcq",
    "options": [{"text": t, "correct": t == "right", "rationale": "r"} for t in ("right", "w1", "w2", "w3")],
}
ORDERING = {"id": "X1-A-02", "type": "ordering", "steps": [{"text": f"s{i}", "rationale": "r"} for i in range(5)]}


def test_display_order_is_deterministic():
    assert display_options(MCQ) == display_options(dict(MCQ))
    assert [o["text"] for _, o in display_options(MCQ)] != [] and len(display_options(MCQ)) == 4


def test_correct_answer_points_at_the_correct_option():
    letter = correct_answer(MCQ)
    assert dict(display_options(MCQ))[letter]["text"] == "right"


def test_ordering_answer_spells_the_authored_order():
    shown = dict(display_steps(ORDERING))
    answer = correct_answer(ORDERING)
    assert [shown[letter]["text"] for letter in answer] == [f"s{i}" for i in range(5)]
