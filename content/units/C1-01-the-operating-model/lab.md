# Lab — Why does this rule exist?

## Goal

Trace three rules in orchestration's `CLAUDE.md` back to the `DECISIONS.md` entries that
explain them.

## Environment

A local clone of `aisdata-team/orchestration` (read-only, used for `grep`), or GitHub's file
view with Ctrl-F. Don't open `DECISIONS.md` and scroll through it; it is 1.3 MB.

## Steps

1. Clone the repo, or pull if you already have it:
   `git clone https://github.com/aisdata-team/orchestration && cd orchestration`
2. In `CLAUDE.md`, find these three rules and note the date citation at the end of each:
   - **(a)** "Search `DECISIONS.md`, never read it end to end" (under "Before you start").
   - **(b)** The rule that `CLAUDE.md` itself is "a contract" (its opening paragraph).
   - **(c)** "HubSpot jobs and ops are named `hubspot_<verb>_<object>`" (under "Development
     guidance").
3. For each rule, find its entry. Search for the date **together with a keyword**, because one
   date can hold many entries:
   ```bash
   grep -n "^## 2026-08-06" DECISIONS.md          # try this first: see how many there are
   grep -n "^## 2026-08-06.*[Ss]earched" DECISIONS.md
   ```
4. Open the matching entry (`sed -n '<line>,+25p' DECISIONS.md`) and write **one sentence** in
   your own words: why does the rule exist?

## You're done when

For each of (a), (b) and (c) you have the **exact `##` heading line** of the entry, copied
character for character, plus a one-sentence why that the entry supports.

## Evidence

The three heading lines and your three sentences.

## Common mistakes

- **Stopping at the first heading with the right date.** 2026-08-06 alone has more than ten
  entries. Match the topic, not just the date.
- **Paraphrasing the heading.** Copy it exactly. The heading is the identifier, and a
  paraphrase can't be searched for.
- **Explaining the rule instead of its reason.** "Because the file is big" is what; the entry
  tells you why splitting or summarising it was rejected.

## Reset

Nothing to reset. The lab is read-only.

## Stretch

Pick any other rule in `CLAUDE.md` whose citation includes an `RM-NN`. Find that item in
`planning/ROADMAP.md` with `grep -n "RM-NN" planning/ROADMAP.md`. Is it still in the backlog,
or has it shipped?
