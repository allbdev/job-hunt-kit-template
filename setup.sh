#!/bin/bash
# One-time setup. Safe to run again: it never overwrites files in me/.
set -u
KIT="$(cd "$(dirname "$0")" && pwd)"
cd "$KIT" || exit 1

mkdir -p me
for f in $(cd templates/me && find . -type f); do
  [ -e "me/$f" ] || { mkdir -p "me/$(dirname "$f")"; cp "templates/me/$f" "me/$f"; echo "created me/${f#./}"; }
done

mkdir -p ~/.claude/skills
for dir in "$KIT"/skills/*/; do
  name="$(basename "$dir")"
  if [ -L ~/.claude/skills/"$name" ] || [ ! -e ~/.claude/skills/"$name" ]; then
    ln -sfn "$KIT/skills/$name" ~/.claude/skills/"$name"
    echo "linked ~/.claude/skills/$name"
  else
    echo "~/.claude/skills/$name exists and is not a link. Left it alone."
  fi
done

# Block pushes that carry private data (see skills/safe-push).
if [ -d .git ]; then
  git config core.hooksPath .githooks && echo "enabled the pre-push privacy check"
fi

# A private Python for the CV builder. Homebrew Python refuses a global pip install.
if [ ! -x me/.venv/bin/python ]; then
  python3 -m venv me/.venv && me/.venv/bin/pip install -q reportlab && echo "created me/.venv with reportlab"
fi
me/.venv/bin/python -c "import reportlab" 2>/dev/null && echo "ok reportlab" || echo "MISSING reportlab in me/.venv"
command -v pdftotext >/dev/null && echo "ok pdftotext" || echo "MISSING pdftotext: brew install poppler"
command -v claude >/dev/null && echo "ok claude" || echo "MISSING claude CLI"
