---
# Copy this folder to content/units/<ID>-<slug>/ and fill every field.
id: F1-01                      # <skill>-<nn>; the folder name is this id, or starts with "<id>-"
skill: F1                      # a skill id from content/skills.yaml
stage: 0                       # must equal the skill's stage
title: "Selecting and filtering rows"
minutes: 75                    # 15–120; a unit is sized for one sitting (60–90 is the target)
prerequisites: []              # unit ids or skill ids
audience: all                  # all | data | it
skippable: true                # may the diagnostic place a learner out of the reading?
sources:                       # every file a claim below rests on, pinned to the commit you read
  - repo: warehouse
    path: README.md
    commit: "0000000000000000000000000000000000000000"
---

# Selecting and filtering rows

## Why this matters here

One real decision or incident from the stack that this unit's skill would have
prevented or explained. Cite it (`DECISIONS.md` entry heading, or a risk id).
No names, no student or staff identifiers.

## The concept

Short. Link the curated outside course from `content/external.yaml` rather than
re-teaching what it covers well.

## How it looks in our stack

Where this concept lives in the real repos. Every claim cites a file, and every
cited file is listed in `sources` above.

## Lab

See [lab.md](lab.md).

## Check questions

The unit-pool items for this unit live in `content/questions/<skill>.yaml`
(`pool: unit`, `unit: <this id>`).

## Ask the tutor

- Seed prompts a learner could ask the tutor about this unit (sub-project 4).
