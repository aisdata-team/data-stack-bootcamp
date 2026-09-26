# Lab — Your first pull request

## Goal

Make a one-line change on your own branch in the practice repo and open a pull request.

## Environment

The practice repo **`aisdata-team/data-stack-bootcamp-practice`**. It is not part of the
stack, so nothing you do there can break anything. You need write access (the operator
grants it) and `git` installed.

## Steps

1. Clone the repo and move into it:
   ```bash
   git clone https://github.com/aisdata-team/data-stack-bootcamp-practice
   cd data-stack-bootcamp-practice
   ```
2. Create a branch named after your pseudonym:
   ```bash
   git switch -c <your-pseudonym>/first-change
   ```
3. Open `notes.md` and add one line at the end: `- <your pseudonym> was here on <today's date>`.
4. Check what Git sees, then commit:
   ```bash
   git status
   git diff
   git add notes.md
   git commit -m "Add my line to notes.md"
   ```
5. Push the branch: `git push -u origin <your-pseudonym>/first-change`.
6. On GitHub, open a pull request from your branch into `main`. In its description, answer:
   - **(a)** How many lines does the diff add, and how many does it remove?
   - **(b)** Which branch will this PR merge into, and how can you tell from the PR page?
7. Open the PR's **Files changed** tab and compare it with what `git diff` showed in step 4.

## You're done when

The PR is open, **Files changed** lists exactly one file (`notes.md`), and the description
answers (a) and (b).

## Evidence

The PR's URL and your two answers. The operator checks them in the weekly hour.

## Common mistakes

- **Committing on `main`.** `git status` shows `On branch main`. Create the branch
  (step 2) before editing, or run `git switch -c …` now; your uncommitted edit comes with you.
- **`git push` fails with "no upstream branch".** Use the `-u origin <branch>` form from step 5.
- **More than one file changed.** Your editor saved something extra. Run `git status`,
  undo the stray file with `git restore <file>`, and amend or add a new commit.

## Reset

Close the PR **without merging** it ("Close pull request"), then delete your branch from the
PR page. The practice repo is then as it was.

## Stretch

Change a line that someone else added and look at the diff. It shows the old line removed
and your new line added: in a diff, a change is always a removal plus an addition.
