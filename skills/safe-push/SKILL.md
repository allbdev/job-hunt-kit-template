---
name: safe-push
description: Run before every git push from the job hunt kit. Checks that no private data (anything from me/, CVs, PDFs, transcripts, names, contacts, secrets) is in the tracked files or in the commits about to leave the machine, then runs the security-audit skill on those commits. Use it whenever the user says push, publish, open a PR, sync the fork, or "send this to GitHub", and before you run `git push` for any reason. Never push from this repo without it.
---

# Safe push

This repo can be public. `me/` is the only place personal data may live, and it is gitignored.
A push is safe only when both steps below pass. Pushing first and deleting later is not a fix:
the commit stays reachable on GitHub.

## 1. The mechanical check

```bash
skills/safe-push/check.py
```

It reads the personal markers from `me/` (name, email, phone, handles, domains, employers,
home folder) and searches the tracked files and every commit no remote has yet. It also fails
on files inside `me/` or `linkedin/`, on documents, archives and credential files, on new
binary files, and on strings that look like tokens.

Done only when it prints `SAFE TO PUSH`. On `DO NOT PUSH`, stop and fix:

- A private file is tracked: move it into `me/` and `git rm --cached` it.
- The data is in an unpushed commit: rewrite the local history so the commit never contained
  it (reset or rebase), then run the check again. Removing it in a new commit is not enough.
- The data is already on the remote: tell the user. That needs a force-push and their
  explicit yes, and anything secret must be rotated.
- A false alarm (a marker that is really public): show the user the line and let them decide.
  Do not edit the check to make it pass.

## 2. The security audit

Call the `security-audit` skill with the Skill tool. Ask for a focused review, not the full
audit workflow, of exactly what is about to be pushed:

```bash
git log -p HEAD --not --remotes
```

Tell it to look for what the mechanical check cannot see:

- Personal data in any form: real work history, employers, clients, salary or rates, location,
  people's names, recruiter or mentor messages, call notes.
- Job search state: companies applied to, verdicts, scan results, reports, logs.
- Other people's data, such as someone else's profile or message.
- Secrets: tokens, cookies, API keys, session files, signed URLs.
- Examples, tests or docs that quote real data instead of made-up data.
- Shell or agent changes that could send `me/` somewhere (uploads, network calls, loosened
  tool allowlists in `scan/daily-agent.sh`).

If the `security-audit` skill is not installed, do the same review yourself with this list and
say that you did it by hand.

## 3. Push

Push only when step 1 printed `SAFE TO PUSH` and step 2 found nothing. Report both results
to the user in one or two lines. The usual rules still hold: ask before pushing, feature
branches only, never force-push without an explicit yes.

A git pre-push hook (`.githooks/pre-push`, enabled by `setup.sh`) runs step 1 on its own as a
backstop. Never bypass it with `--no-verify`.
