---
id: F3-01
skill: F3
stage: 0
title: "Git and GitHub basics: from a change to a pull request"
minutes: 75
prerequisites: []
audience: all
skippable: true
sources:
  - repo: orchestration
    path: CLAUDE.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
---

# Git and GitHub basics: from a change to a pull request

## Why this matters here

Every change to the data stack, whether code, a dbt model or a line of documentation,
arrives as a **pull request (PR)**. CI checks it, a person reads it, and only then is it
merged into `main` and deployed. The PR is where a reviewer does their work. By stage 3
you will be that reviewer, so reading a PR has to come easily.

One lesson from the operating record shows why the details matter. The orchestration
repo's `CLAUDE.md` says: *"After opening or pushing to a PR, check mergeability BEFORE
waiting on CI. GitHub runs no PR workflows on a conflicted head, so a conflicted PR shows
zero checks and a session that waits for them waits forever."* A merge conflict doesn't
look like a failure. It looks like nothing happening.

## The concept

Work through the GitHub Docs **Hello World** tutorial first (link in
`content/external.yaml`, about 30 minutes). It covers the five ideas this unit uses:

- **Repository:** the project and its full history.
- **Branch:** your own line of work, separate from `main` until it is merged.
- **Commit:** a saved snapshot with a message saying what changed and why.
- **Pull request:** a proposal to merge your branch into `main`, with its diff, its CI checks
  and its conversation.
- **Diff:** the lines added (`+`, green) and removed (`-`, red) by a change.

You will also use `git` on the command line: `clone`, `switch -c`, `add`, `commit` and `push`.

## How it looks in our stack

- There are three repos: `orchestration` (Dagster, the VM, the ledger), `warehouse` (the dbt
  models) and `strategic-planning` (rubrics and plans). Most work happens on a branch and
  arrives as a PR.
- **Every PR description carries a `## Requirements` section**, quoting the original ask
  rather than paraphrasing it, and **ends with a "Verification status" block** saying what CI
  proved and what still needs a real run. That rule is in orchestration's `CLAUDE.md` under
  "Ways of working". Open any recently merged PR in `aisdata-team/orchestration` and you will
  find both sections.
- CI runs on every PR: lint, tests, and checks on the ledger itself. A green PR proves the code
  loads and its tests pass. It does **not** prove the change works against real data (same file,
  "CI, linting and tests").

## Lab

See [lab.md](lab.md). You'll make a change in the practice repo and open a PR.

## Check questions

Three quick questions after the lab (`content/questions/F3.yaml`, pool `unit`).

## Ask the tutor

- "What is the difference between a commit and a push?"
- "Why would a PR show zero CI checks?"
- "What does a line starting with `-` mean in a diff?"
