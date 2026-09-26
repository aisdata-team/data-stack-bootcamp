# Lab — Three questions, verified

## Goal

Use Claude Code read-only to answer three questions about the stack, check every answer against
its source, and record at least one answer that was wrong or couldn't be sourced.

## Environment

Claude Code with read access to `aisdata-team/orchestration` and `aisdata-team/warehouse`. The
operator sets this up. **Work in plan mode, or start by telling it: "Do not edit any files or run
anything that changes state."** Never paste real student or staff data into a prompt.

## Steps

1. Start a session with both repos attached and state the read-only rule.
2. Ask each question and **ask for the file and section** behind the answer:
   - **(a)** "How does the nightly production run get the dbt code, and why that way?"
   - **(b)** "What does the `/next-steps` skill do, and does it edit anything?"
   - **(c)** "Which BigQuery project holds the production marts?"
3. For each answer, open the cited file yourself and find the sentence that supports it. Mark
   the answer **verified**, **wrong** or **unsourced**.
4. If all three verify, keep going with harder questions of your own until you get one that is
   wrong or that Claude can't source. There will be one. Good places to look: exact numbers,
   dates, and anything about "the latest" state.

## You're done when

You have three answers marked **verified**, each with the file and quoted sentence that
supports it, **and** one answer marked **wrong** or **unsourced**, with what you checked.

## Evidence

The four questions, Claude's short answers, your marks, and the supporting or contradicting
quotes.

## Common mistakes

- **Accepting the citation without opening it.** A cited file that doesn't say what's claimed
  is the most common failure, and the one this lab exists to catch.
- **Checking against another chat answer.** Only the file counts.
- **Letting it "just fix" something it spotted.** Stay read-only. Note it and tell the operator
  instead.

## Reset

End the session. Nothing was changed, so there is nothing to undo; if something was, tell the
operator.

## Stretch

Ask the same question twice in fresh sessions, worded differently. Do the answers agree? Do they
cite the same file?
