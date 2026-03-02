#!/usr/bin/env zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"
source .venv/bin/activate

if ! pip show pyinstaller >/dev/null 2>&1; then
  pip install pyinstaller
fi

rm -rf build dist
pyinstaller VoidBreaker.spec --noconfirm

ARCADE_VERSION_PATH="dist/VoidBreaker.app/Contents/Resources/arcade/VERSION"
if [[ -d "$ARCADE_VERSION_PATH" ]]; then
  if [[ -f "$ARCADE_VERSION_PATH/VERSION" ]]; then
    TEMP_VERSION_FILE="${ARCADE_VERSION_PATH}.tmp"
    mv "$ARCADE_VERSION_PATH/VERSION" "$TEMP_VERSION_FILE"
    rm -rf "$ARCADE_VERSION_PATH"
    mv "$TEMP_VERSION_FILE" "$ARCADE_VERSION_PATH"
  else
    rm -rf "$ARCADE_VERSION_PATH"
  fi
fi

APP_EXECUTABLE="dist/VoidBreaker.app/Contents/MacOS/VoidBreaker"
if [[ ! -x "$APP_EXECUTABLE" ]]; then
  echo "Build succeeded but executable was not found at: $APP_EXECUTABLE" >&2
  exit 1
fi

du -sh dist/VoidBreaker.app

echo "Build completed successfully: $REPO_ROOT/dist/VoidBreaker.app"
