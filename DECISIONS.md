# Decisions

The course's decision record: one file, newest entries first, dated headings that never move.
An entry holds the decision, the why in about 5 lines, and a `Revisit if`.

## 2026-09-26 (c) — Question banks are reviewed by an agent that did not write them, and a long answer key is flagged

**Decision.**
- **Agent-drafted items reach a PR only after an independent review** by a fresh agent that did
  not write them. The reviewer checks, per item, that the key is right against its pinned
  sources, that no second option can be defended, that the key is not given away, and that
  forms A and B are parallel.
- **`validate_content.py` flags any item whose correct option is more than 1.5× the length of
  its longest distractor.** The flag is advisory and never fails the build.

**Why.**
- In the first review the keys were all correct, but the correct option was conspicuously the
  longest in 45 of 78 items. It also found seven items with a second defensible answer, and
  four unit checks that duplicated diagnostic items.
- A self-review shares the author's blind spots — the correlated-reasoning half of ORCH-102,
  which a diagnostic built to measure people can't afford.
- The length flag is advisory because a precise key is sometimes necessarily longer.

**Revisit if** a later review finds nothing across a whole stage. The flag can then carry the
check alone and the full independent review can become spot checks.

## 2026-09-26 (b) — Release 0 scaffolding: the item schema, the placement thresholds, and a drift check that fails closed

**Decision.**
- **The question bank is one YAML file per skill** with three disjoint pools: `A` (entry
  diagnostic), `B` (exit retake) and `unit` (unit checks). Each form holds exactly 2 confidence
  statements and 3 check items.
- **Options and ordering steps are shown in a shuffled order seeded on the item id**
  (`bank.display_options` / `display_steps`). The scorer reads letters back through the same
  function.
- **"I don't know" is never authored.** It is always added, and the validator rejects an authored
  one.
- **Placement** (`scripts/score.py`, the reference the app must match):
  - *confident* = mean confidence ≥ 4.0 ("Agree"); *passed* = at least ⅔ correct (2 of 3, or 1
    of 1 on the screener);
  - confident and passed → `place_out`; passed only → `prove_it`; confident, not passed, with a
    wrong answer → `take_flagged`; otherwise → `take`;
  - an "I don't know" is never a misconception;
  - from stage 2 on, labs are always required.
- **`check_source_drift.py` fails closed.** It exits 0 only when every pinned source was read and
  none changed; 1 on drift; 2 when not run or incomplete.

**Why.**
- Authors put the correct option first, so authored order would leak answers.
- An authored "I don't know" can be forgotten, and without it guesses count as knowledge. That
  would erase the difference between a wrong answer and not knowing, which is the whole point
  of flagging misconceptions.
- A drift check that reports clean when it could not look is the fail-open shape
  orchestration's `CLAUDE.md` rules out for any check.
- The thresholds come from the approved spec.

**Revisit if** the pilot shows the 4.0 or ⅔ thresholds misplacing people. Change them in
`score.py` and its tests first, then in the app.

## 2026-09-26 — The course exists: ten decisions made with the operator

**Decision.** Build the course as designed in the orchestration repo's
`docs/superpowers/specs/2026-09-25-data-stack-training-course-design.md` (RM-244), in this repo.
The decisions it records:
1. **Graduate outcomes:** all three, staged — partner, then operator, then contributor.
2. **Delivery:** short readings, hands-on labs, and a weekly hour with the operator for sign-off.
3. **Audience:** the data team and IT together, with two entry points.
4. **Placement:** a Likert confidence plus check-question diagnostic.
5. **Platform:** a new Firebase app, built with Claude Code, with a Gemini tutor.
6. **Build order:** content, then the app, then the sandbox, then the tutor.
7. **Access:** stage-2 graduates keep standing production access.
8. **Stage 3:** review first; authoring is an optional stage 4.
9. **Claude Code:** its own strand (C1–C7) through every stage.
10. **App roles:** admin, learner and observer.

**Privacy (part of this entry):**
- No real student or staff data appears in content.
- Diagnostic responses are never committed.
- Results are never used for performance evaluation.

**Why.**
- Risk ORCH-102: one operator, and runbooks no second person has ever used.
- The course produces the backup operators and independent reviewers that risk needs. Its
  stage-2 capstone is RM-234 performed for real.

**Revisit if** the Release-1 pilot shows the unit size or the diagnostic is wrong for the
learners it was built for.
