# Job hunt kit

- Personal data lives only in `me/`. It is gitignored. Never commit it, never copy it into `templates/`, `cv/`, `scan/` or `skills/`.
- New user: follow `SETUP.md`.
- A job ad or job link: use the `job-fit` skill.
- `me/work-history.txt` is the source of truth. Never put a fact on a CV or letter that is not in it.
- Never add a tool to a CV because an ad lists it.
- CV work is done only when `cv/build.sh` prints `ALL GOOD`.
- No em or en dashes in anything the user sends out.
- Nothing about the job search goes public: no posts, no public repos.

## Hard rule: private data never enters git

This repo can be public. No exceptions, and no "just for now".

- Everything personal goes in `me/` and nowhere else: CVs, PDFs, profile exports, transcripts, call notes, mentor or recruiter messages, screenshots, drafts about the user, other people's profiles, scan state.
- Never create a personal file or folder outside `me/`, not even untracked. If one shows up, move it into `me/`.
- Never weaken the `/me/` line in `.gitignore`, never `git add -f` an ignored file, never `git add -A` or `git add .`.
- Tracked files (`templates/`, `cv/`, `scan/`, `skills/`, docs, tests, commit messages) use made-up data only. No real name, contact, employer, client, pay or company applied to.
- Before every `git push`, use the `safe-push` skill: `skills/safe-push/check.py` must print `SAFE TO PUSH`, then the `security-audit` skill reviews the outgoing commits. Never push with `--no-verify`.
- If private data is found in a commit, stop and tell the user. Fix the history before pushing. Deleting it in a later commit does not remove it.
