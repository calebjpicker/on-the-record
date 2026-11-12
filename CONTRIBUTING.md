# Contributing

Thanks for helping. This project is at the design stage, so the most useful
contributions right now are review, research and corrections as much as code.
The [README](README.md) lists where help is wanted.

## Ground rules

- **Nonpartisan.** No ratings, endorsements, advocacy or calls to action about
  any member, party or bill. Wording stays neutral.
- **Everything has a source.** A declaration, a claim about chamber rules or a
  data-source note needs a link someone else can check.
- **Nothing is silently changed.** Positions are corrected by adding to their
  history, never by rewriting it.
- **No real declarations in examples.** Mockups, tests and fixtures use
  fictional members and bills, clearly labeled as sample data.
- **No secrets in the repository.** API keys and mailbox credentials stay out
  of commits.

## How work is organized

`main` is always the reviewed, working state. Nobody commits to it directly.

1. **One branch per change.** Name it `<type>/<short-description>`:

   | Type | For |
   |---|---|
   | `feat/` | new functionality |
   | `fix/` | bug fixes |
   | `data/` | changes to files under `data/` |
   | `docs/` | documentation and research notes |
   | `design/` | mockups and wording |
   | `chore/` | tooling and maintenance |

   Example: `feat/house-schedule-ingest`.

2. **One worktree per branch.** A git worktree is a second checkout of the same
   repository in its own folder, so several branches can be open at once
   without stashing or switching. Worktrees live under `.worktrees/`, which is
   ignored by git.

   ```bash
   git fetch origin main
   git worktree add -b feat/house-schedule-ingest .worktrees/house-schedule-ingest origin/main
   cd .worktrees/house-schedule-ingest
   ```

3. **Commit and push the branch.**

   ```bash
   git push -u origin feat/house-schedule-ingest
   ```

4. **Open a pull request into `main`.** Say what changed and why, and link the
   sources for any factual claim. Open it as a draft if it is not ready for
   review.

5. **After it merges, remove the worktree and the branch.**

   ```bash
   git worktree remove .worktrees/house-schedule-ingest
   git branch -d feat/house-schedule-ingest
   ```

Using plain branches without worktrees is fine too. The rule that matters is
one branch per change, merged through a pull request.

## Reporting an error

Open an issue with the page or file, what is wrong, and a source for the
correct information.
