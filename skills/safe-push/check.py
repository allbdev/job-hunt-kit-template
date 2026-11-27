#!/usr/bin/env python3
"""Refuse a push that would publish private data.

    skills/safe-push/check.py                    commits on HEAD that no remote has yet
    skills/safe-push/check.py <rev-list args>    a specific set of commits

Checks the tracked files and every outgoing commit (also files added and later
deleted, which still ship in history). The personal markers are read from me/
at run time, so nothing personal is written in this file.
Prints SAFE TO PUSH and exits 0, or lists the problems and exits 1.
"""
import os
import re
import subprocess
import sys
import unicodedata

BLOCKED_EXT = (
    ".pdf", ".doc", ".docx", ".odt", ".rtf", ".pages", ".xls", ".xlsx", ".numbers",
    ".pem", ".key", ".p12", ".sqlite", ".sqlite3", ".db", ".zip", ".har",
)
BLOCKED_NAME = re.compile(r"(^|/)(\.env(\..*)?|id_rsa|id_ed25519|credentials\.json|cookies?\.(json|txt))$")
PRIVATE_DIRS = ("me/", "linkedin/")
SECRET = re.compile(
    r"(-----BEGIN [A-Z ]*PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}|\bgh[pousr]_[A-Za-z0-9]{30,}"
    r"|\bAKIA[0-9A-Z]{16}\b|\bxox[baprs]-[A-Za-z0-9-]{10,})"
)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, errors="replace").stdout


def fold(text):
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def markers(root):
    """Personal strings found in me/, minus anything the public templates also contain."""
    profile = read(os.path.join(root, "me", "profile.py"))
    history = read(os.path.join(root, "me", "work-history.txt"))
    found = set()

    for text in (profile, history):
        found.update(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text))
        for phone in re.findall(r"\+\d[\d ()-]{8,}\d", text):
            found.add(phone)
            found.add(re.sub(r"\D", "", phone))

    name = re.search(r'^NAME\s*=\s*"([^"]+)"', profile, re.M)
    if name:
        found.add(name.group(1))

    links = history.split("== Links ==", 1)[1].split("\n==", 1)[0] if "== Links ==" in history else ""
    contact = re.search(r"^CONTACT\s*=\s*\((.*?)\)\s*$", profile, re.M | re.S)
    for text in (links, contact.group(1) if contact else ""):
        for url in re.findall(r"(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[\w./-]+)?", text, re.I):
            host, _, path = url.partition("/")
            if re.search(r"(^|\.)(linkedin|github|gitlab|x|twitter)\.com$", host, re.I):
                handle = path.rstrip("/").split("/")[-1]
                if len(handle) >= 5:
                    found.add(handle)
            elif not re.search(r"(^|\.)(gmail|outlook|hotmail|yahoo|icloud|proton)\.", host, re.I):
                found.add(host)

    # "== Title | Company | dates | ... ==" headings in the work history.
    for heading in re.findall(r"^== (.+) ==$", history, re.M):
        parts = [p.strip() for p in heading.split("|")]
        if len(parts) >= 3 and len(parts[1]) >= 5:
            found.add(parts[1])

    home = os.path.expanduser("~")
    if home.count("/") >= 2:
        found.add(home)

    public = fold("".join(
        read(os.path.join(dirpath, f))
        for dirpath, _, files in os.walk(os.path.join(root, "templates"))
        for f in files
    ))
    out = {fold(m).strip() for m in found}
    return sorted(m for m in out if len(m) >= 5 and m not in public)


def main():
    root = git("rev-parse", "--show-toplevel").strip()
    if not root:
        print("Not inside a git repository.")
        return 1
    os.chdir(root)
    revs = sys.argv[1:] or ["HEAD", "--not", "--remotes"]
    problems = []

    if not os.path.isdir("me"):
        print("  note: no me/ folder here, so there are no personal markers to search for.")
    if subprocess.run(["git", "check-ignore", "-q", "me/x"]).returncode != 0:
        problems.append(".gitignore no longer ignores me/")

    tracked = git("ls-files").splitlines()
    outgoing = sorted(set(filter(None, git("log", "--name-only", "--format=", *revs).splitlines())))
    for path, where in [(p, "tracked") for p in tracked] + [(p, "outgoing commit") for p in outgoing]:
        low = path.lower()
        if low.startswith(PRIVATE_DIRS):
            problems.append(f"{where}: {path} is inside a private folder")
        elif low.endswith(BLOCKED_EXT) or BLOCKED_NAME.search(low):
            problems.append(f"{where}: {path} is a document, archive or credential file")

    for line in git("log", "--numstat", "--format=", "--diff-filter=AM", *revs).splitlines():
        if line.startswith("-\t-\t"):
            problems.append(f"outgoing commit: binary file {line.split(chr(9), 2)[2]} (check it by hand, or keep it in me/)")

    marks = markers(root)

    def scan(label, text):
        folded = fold(text)
        for m in marks:
            if m in folded:
                problems.append(f"{label}: contains personal marker {m!r}")
        if SECRET.search(text):
            problems.append(f"{label}: looks like a secret or token")

    for path in tracked:
        scan(f"tracked path {path}", path)
        blob = read(path)
        if "\0" not in blob[:8000]:
            for n, line in enumerate(blob.split("\n"), 1):
                scan(f"{path}:{n}", line)

    commit, path = "", ""
    for line in git("log", "-p", "--no-color", "--format=@@commit %h %an <%ae> %s%n%b", *revs).split("\n"):
        if line.startswith("@@commit "):
            commit = line.split()[1]
            # The author name and email are public on purpose; check only the message.
            scan(f"commit {commit} message", line.split("> ", 1)[-1])
        elif line.startswith("+++ "):
            path = line[6:]
            scan(f"commit {commit} path {path}", path)
        elif line.startswith("+") and not line.startswith("+++"):
            scan(f"commit {commit} {path}", line[1:])
        elif commit and not line.startswith(("-", " ", "diff ", "index ", "@@", "new file", "deleted file",
                                             "similarity", "rename", "old mode", "new mode", "Binary", "\\")):
            scan(f"commit {commit} message", line)

    problems = list(dict.fromkeys(problems))
    count = len(git("rev-list", *revs).split())
    print(f"  checked {len(tracked)} tracked files, {count} outgoing commits, {len(marks)} personal markers")
    if problems:
        print("  DO NOT PUSH:\n    " + "\n    ".join(problems[:60]))
        if len(problems) > 60:
            print(f"    ... and {len(problems) - 60} more")
        return 1
    print("  SAFE TO PUSH")
    return 0


if __name__ == "__main__":
    sys.exit(main())
