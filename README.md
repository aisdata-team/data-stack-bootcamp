# Data-stack bootcamp

A staged, hands-on course that brings data-team and IT colleagues up to speed on the
AIS data stack. The stack is Dagster, dlt, BigQuery and dbt, on one GCP VM, built with
Claude Code. Graduates become **backup operators** who keep production access, and
**reviewers** who can independently check changes made with Claude Code.

- **Design:** the approved spec in the orchestration repo,
  `docs/superpowers/specs/2026-09-25-data-stack-training-course-design.md`.
- **Roadmap item:** RM-244.
- **Decisions:** [`DECISIONS.md`](DECISIONS.md).

## Stages

| Stage | A graduate can… | Who starts here |
|---|---|---|
| **0 · Foundations** | work at the level the rest of the course assumes (SQL, command line, Git, Docker, GCP) | Data team; IT places out of most via the screener |
| **1 · Partner** | explain the stack end to end, trace a field from dashboard to source, find why something is the way it is | Everyone |
| **2 · Operator** | run and recover the stack, and keep standing production access | Everyone |
| **3 · Reviewer** | independently review Claude-authored changes against their requirements and the conventions | Everyone who continues |
| **4 · Author** *(optional)* | author changes by hand or by directing Claude Code | Anyone who wants it |

Every skill is listed in [`content/skills.yaml`](content/skills.yaml).

## How a unit works

A unit takes 60–90 minutes, one sitting. Each has three parts:
1. A short reading (`unit.md`).
2. A hands-on lab (`lab.md`) with an observable "you're done when".
3. A few check questions.

**The diagnostic** runs at the start of each stage. It compares your confidence with a
few check questions and places you, skill by skill:
- **place out** — the reading is optional;
- **prove it** — do the lab only;
- **take it**.

You retake it at the end of the stage. **Results are for placement and are never used
for performance evaluation.**

## Layout

```
content/
  skills.yaml          the skills map
  units/<ID>-<slug>/   unit.md + lab.md
  questions/<SKILL>.yaml   the question bank: form A, form B, unit checks
  _templates/          copy these to start a unit or a question file
scripts/
  validate_content.py  structural checks on all content (CI)
  score.py             the placement rule: score one diagnostic response
  check_source_drift.py  which content cites a source file that has since changed
tests/                 pytest for the scripts
```

## Commands

```bash
pip install -r requirements-dev.txt
python -m pytest -q
python scripts/validate_content.py
python scripts/score.py responses/<pseudonym>-<stage>-<form>.yaml   # responses/ is gitignored
BOOTCAMP_SOURCES_TOKEN=… python scripts/check_source_drift.py
```

## CI

- **`validate`** runs ruff, pytest and the content validator on every push and PR. It is the
  required check.
- **`drift`** runs weekly and is advisory. It needs the `BOOTCAMP_SOURCES_TOKEN` secret: a
  read-only token for `orchestration` and `warehouse`. Without it the run goes red with
  "NOT RUN", never quietly green.
