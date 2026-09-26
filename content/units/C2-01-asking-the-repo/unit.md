---
id: C2-01
skill: C2
stage: 1
title: "Asking the repo: Claude Code as a reader, and checking what it tells you"
minutes: 90
prerequisites: [C1-01]
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
    path: .github/workflows/test-intent-review.yml
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
  - repo: orchestration
    path: .claude/skills/next-steps/SKILL.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
  - repo: orchestration
    path: .claude/skills/project-analysis/SKILL.md
    commit: "ea713797fe70d68779f9116577dda81dddcc4e6f"
---

# Asking the repo: Claude Code as a reader, and checking what it tells you

## Why this matters here

Risk **ORCH-102** records a hard number. Of the register's 30 realised risks, **21 were code
defects or wrong assumptions that reached production with CI green**. The tests encoded the
same assumption as the code. When the same reasoning writes the answer and the check, the
check can't catch it.

The same applies to you asking Claude Code about the stack. Its answers are usually right and
always sound confident. An answer you haven't checked against a file is a lead to follow, not
a fact.

## The concept

Claude Code is an agent that can read the repository, search it and run commands. Used
**read-only**, meaning plan mode or questions with no edits allowed, it is a fast way to find
where something lives and why. The discipline is:

1. **Ask for the source.** "Which file and section says that?"
2. **Open the source yourself** and confirm it says what Claude claims.
3. **Treat anything without a source as unverified,** however plausible it sounds.

## How it looks in our stack

- Each session loads `CLAUDE.md` automatically. That is why Claude knows the house rules, and
  why those rules carry citations you can check (unit C1-01).
- The repos contain **skills**, packaged instructions in `.claude/skills/*/SKILL.md`. Some only
  report and some rank. For example, `/project-analysis` produces a read-only health report,
  and `/next-steps` ranks the backlog to recommend what to do next. Read the `description:`
  line at the top of each `SKILL.md`.
- In this unit you only read. Stage 2 (unit C4) covers what Claude Code may and may not do
  near production.

## Lab

See [lab.md](lab.md). You'll ask Claude Code three questions and verify every answer.

## Check questions

Three quick questions after the lab (`content/questions/C2.yaml`, pool `unit`).

## Ask the tutor

- "How do I tell Claude Code not to change anything?"
- "What should I do when Claude cites a file that doesn't say what it claims?"
- "What is the difference between a skill that reports and one that ranks?"
