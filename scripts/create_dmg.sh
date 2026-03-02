#!/usr/bin/env zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

APP_BUNDLE="$REPO_ROOT/dist/VoidBreaker.app"
DMG_OUTPUT="$REPO_ROOT/dist/VoidBreaker.dmg"
VOLUME_NAME="VoidBreaker"
ICON_FILE="$REPO_ROOT/assets/icon.icns"

if [[ ! -d "$APP_BUNDLE" ]]; then
  echo "Missing app bundle: $APP_BUNDLE" >&2
  echo "Run ./scripts/build_app.sh first." >&2
  exit 1
fi

rm -f "$DMG_OUTPUT"

if command -v create-dmg >/dev/null 2>&1; then
  echo "Using create-dmg for polished DMG layout..."
  create_dmg_args=(
    --volname "$VOLUME_NAME"
    --window-pos 200 120
    --window-size 600 400
    --icon-size 100
    --icon "VoidBreaker.app" 150 200
    --app-drop-link 450 200
    --no-internet-enable
  )

  if [[ -f "$ICON_FILE" ]]; then
    create_dmg_args+=(--volicon "$ICON_FILE")
  fi

  create-dmg \
    "${create_dmg_args[@]}" \
    "$DMG_OUTPUT" \
    "$APP_BUNDLE"
else
  echo "create-dmg not found; falling back to hdiutil..."

  tmp_dmg_dir="$(mktemp -d)"
  cleanup() {
    rm -rf "$tmp_dmg_dir"
  }
  trap cleanup EXIT

  cp -R "$APP_BUNDLE" "$tmp_dmg_dir/"
  ln -s /Applications "$tmp_dmg_dir/Applications"

  hdiutil create \
    -volname "$VOLUME_NAME" \
    -srcfolder "$tmp_dmg_dir" \
    -ov \
    -format UDZO \
    "$DMG_OUTPUT"
fi

hdiutil verify "$DMG_OUTPUT"

echo "DMG created successfully: $DMG_OUTPUT"
du -sh "$DMG_OUTPUT"
