---
id: C1-01
skill: C1
stage: 1
title: "The operating model: one operator, Claude Code, and a written record"
minutes: 75
prerequisites: []
audience: all
skippable: true
sources:
  - repo: orchestration
    path: CLAUDE.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
  - repo: orchestration
    path: docs/risk-register.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
  - repo: orchestration
    path: DECISIONS.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
  - repo: orchestration
    path: planning/ROADMAP.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
---

# The operating model: one operator, Claude Code, and a written record

## Why this matters here

Since May 2026 the stack has been built and run by **one person working with Claude Code**.
The risk register scores that as risk **ORCH-102**. Claude writes the code, the tests, the
record of why and the risk scores, and the operator is the only independent judgement in the
loop.

The stated protection against losing that one person is the written record. According to
ORCH-102, only one human has ever read it. This course is part of changing that, and you are
the second reader.

## The concept

Anyone who takes over a system needs to know **why** it is the way it is, not just **what** it
is. Otherwise they will "fix" deliberate choices back into mistakes. This stack keeps
decisions, plans and risks in plain files next to the code, where both people and Claude Code
can read them.

## How it looks in our stack

Five documents, each with one job:

| File | Its job | Who reads it |
|---|---|---|
| `CLAUDE.md` | **A contract.** Rules, each with a one-line why and a citation. Claude Code loads it on every turn, so it is kept short. | Claude Code, every session, and you |
| `README.md` | **The index.** It links to a page for each pipeline and area. | Anyone starting on a task |
| `DECISIONS.md` | **The ledger.** One dated entry per decision, holding the decision, the why and a "Revisit if". About 370 entries and 1.3 MB, so it is **searched, never read end to end**. | Whoever is about to change something |
| `planning/ROADMAP.md` | **The backlog.** RM-NN items, ranked: risk first, then value per effort. | Whoever decides what to do next |
| `docs/risk-register.md` | **The risks.** ORCH-NN and WH-NN rows, each scored likelihood × severity, with mitigations. | Same |

A citation such as **(2026-08-06)** after a `CLAUDE.md` rule points to a `## 2026-08-06 …`
heading in `DECISIONS.md`. Headings never move, so the citation keeps working. When several
decisions fall on the same date they are lettered: `(b)`, `(c)`, and so on. All of this is in
orchestration's `CLAUDE.md`, "Before you start" and "Documentation".

## Lab

See [lab.md](lab.md). You'll trace three rules back to the decisions behind them.

## Check questions

Three quick questions after the lab (`content/questions/C1.yaml`, pool `unit`).

## Ask the tutor

- "Why is CLAUDE.md kept short when DECISIONS.md is so long?"
- "What would go wrong if someone deleted old DECISIONS entries to tidy up?"
- "What is ORCH-102 worried about, in one sentence?"
