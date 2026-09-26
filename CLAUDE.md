# CLAUDE.md

A contract: rules, a one-line why, a citation. Reasoning lives in `DECISIONS.md`.

## Sessions

- **Attach `orchestration` and `warehouse` alongside this repo.** Units are drafted from
  them. They are **read-only here**: never push to them from bootcamp work.
- **Interactive: clarify if in doubt. Autonomous: never block.** In an autonomous run,
  take the conservative reading and open the PR description with "Decisions made
  without you".

## Authoring rules

- **No real student or staff data anywhere.** Case studies from the source repos'
  `DECISIONS.md` are scrubbed of names and identifiers, and examples use synthetic
  values. Learners copy what they see (2026-09-26).
- **Every factual claim about the stack cites a file, and the file is in the unit's
  `sources`, pinned to the commit you read** (`git -C ../orchestration rev-parse HEAD`).
  `check_source_drift.py` can only flag what is pinned (2026-09-26).
- **Start from `content/_templates/`.** The validator requires every section they carry.
  A test builds its fixture from the templates, so the two cannot drift apart.
- **Never author an "I don't know" option.** The renderer and the app always add it,
  and the validator rejects an authored one (2026-09-26 (b)).
- **A lab's "You're done when" is observable** — a row count, a green run, a named file
  in a diff. Never "you understand X".
- **Units are 60–90 minutes.** If a draft runs longer, split it; never compress the lab.

## Data about learners

- **Diagnostic responses live in `responses/`, which is gitignored. Never commit them.**
  Pilot findings are committed only as anonymised template and content fixes, with no
  names and no scores (2026-09-26).

## Code

- **`scripts/score.py` is the reference placement rule.** The app must match it; change
  the rule there first, with its tests (2026-09-26 (b)).
- **The drift check fails closed.** No token, an unreadable source, or no sources is
  never "clean" (2026-09-26 (b)).
- **Checks before pushing:** `ruff check scripts tests`, `ruff format --check scripts tests`,
  `python -m pytest -q`, `python scripts/validate_content.py`.
- **Dependencies are fully pinned** in `requirements-dev.txt`. Run `pip-audit` before
  adding or bumping one.

## Documentation

- **`DECISIONS.md` is one file**, with dated `## YYYY-MM-DD [(x)]` headings that never move.
  An entry holds the decision, the why in about 5 lines, and a `Revisit if`.
- **Progress is tracked in the orchestration repo as RM-244** (`planning/ROADMAP.md`).
  Update its `Status` at each release close-out, following that repo's `_Last updated_`
  rule.
