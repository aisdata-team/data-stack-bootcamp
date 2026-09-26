# Release 1 pilot — protocol

The pilot tests the **format** of the course (unit size, lab template, diagnostic items) on two
real learners before the rest of the course is written. It needs neither the app nor the
sandbox.

## Who

- **The operator** runs the weekly hour, signs off labs and scores diagnostics.
- **Two learners:** one from the data team, one from IT.

## Before the pilot (operator)

0. **Check every link in `content/external.yaml`** for the pilot skills (F1–F5, P2, P4). Open
   each one, confirm it is live, free and still covers `parts`, then set `checked:` to the date.
   Remove anything dead or paywalled. The links could not be opened when they were chosen.
1. **Create `aisdata-team/data-stack-bootcamp-practice`** (private), containing a `README.md`
   and a `notes.md` with a few lines. Give both learners *Write* access.
2. **Give both learners** *Read* access to `orchestration` and `warehouse`, Claude Code access,
   and a GitHub account in the org.
3. **Take every diagnostic yourself first**, forms A **and** B for stages 0 and 1:
   ```bash
   python3 scripts/render_diagnostic.py --stage 0 --form A > /tmp/s0A.md   # and B, and stage 1
   ```
   Answer on paper, transcribe to `responses/operator-s0-A.yaml` (format in `scripts/score.py`),
   then run:
   ```bash
   python3 scripts/score.py responses/operator-s0-A.yaml
   ```
   **You should score close to 100%. Every item you miss or find ambiguous gets fixed before any
   learner sees it.** Keep a list; it is the pilot's first finding.

## The pilot

| Week | Data-team learner | IT learner |
|---|---|---|
| 1 | Stage 0 **form A** + stage 1 **form A** (about 60 min) | Stage 0 **screener** + stage 1 **form A** (about 35 min) |
| 2 | Unit F3-01 | Unit F3-01 (or skip it if the screener placed them out of F3) |
| 3 | Unit P1-01 | Unit P1-01 |
| 4 | Unit C1-01 | Unit C1-01 |
| 5 | Unit C2-01 | Unit C2-01 |
| 6 | Retake on **form B** (the same stages as week 1) | Retake on **form B** |

A light week can hold one unit and a heavy week two, so compress the schedule when it fits.

- **Print forms** with `render_diagnostic.py`. Print the answer key (`--key`) for yourself only.
- **Score** each response with `score.py`. Go through each placement with the learner in the
  weekly hour, including any flagged misconception, which shows the wrong answer they chose and
  why it is tempting.
- **Sign off each lab** against its "You're done when" and "Evidence" sections.

## What to record, per learner and per unit

- **Actual minutes** against the unit's `minutes:`.
- **Every question the learner had to ask you:** each one is a gap in the unit.
- **Every item that misfired:** ambiguous, two defensible answers, or an answer given away by
  its wording.
- **Whether the lab's "You're done when" was clear** without asking.

## Privacy

- **Responses stay in `responses/`, which is gitignored. Never commit them**, and delete them
  after the pilot.
- **Commit only anonymised fixes.** Changes to units, labs and items, plus a short
  `pilot/findings.md` listing what was changed and why. No names, no pseudonyms, no scores.
- **Tell learners before they start:** results are for placement, and are **never** used for
  performance evaluation.

## Success criterion (from the spec)

The pilot **passes** when:
- both learners finish each unit within **1.5×** its estimated minutes, **and**
- every item the operator missed or flagged has been fixed.

## Close-out

- **Bootcamp `DECISIONS.md`:** an entry recording the result as
  `🎯 **FIRST RUN PASSED**` or `🎯 **FIRST RUN FAILED** — <what it found>`, plus the template
  changes the pilot forced.
- **Orchestration `planning/ROADMAP.md`:** update RM-244's `Status` with the measured result and
  name release 2's blockers (the app, and the sandbox BigQuery dataset).
