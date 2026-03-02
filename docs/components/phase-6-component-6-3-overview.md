# Phase 6 Component 6.3 — DMG Creation & Distribution Packaging

## Summary

Component 6.3 is complete. DMG packaging automation is implemented with a polished-tool first strategy (`create-dmg`) and a guaranteed fallback (`hdiutil`), plus future release documentation for macOS code signing and notarization.

## Deliverables Completed

- Created executable DMG build script: `scripts/create_dmg.sh`
- Created signing/notarization guide: `docs/code-signing-guide.md`
- Built release DMG: `dist/VoidBreaker.dmg`

## Packaging Implementation Notes

### `scripts/create_dmg.sh`

- Validates prerequisite app bundle exists at `dist/VoidBreaker.app`
- Removes stale DMG output before packaging
- Uses `create-dmg` when available for icon/layout polish
- Falls back to `hdiutil` (`UDZO`) with:
  - `VoidBreaker.app` copied into a temporary staging directory
  - `Applications` symlink (`/Applications`) created in DMG root
- Runs `hdiutil verify` on generated artifact
- Prints output path and human-readable DMG size

### `docs/code-signing-guide.md`

- Documents Developer ID code signing workflow (`codesign --deep --options runtime`)
- Documents notarization workflow (`notarytool submit --wait`)
- Documents stapling (`xcrun stapler staple` + validation)
- Documents unsigned v1.0 Gatekeeper workaround for end users
- Includes optional secure keychain-profile setup for notary credentials

## Validation Runbook and Results

### DMG build

- Command: `source .venv/bin/activate && ./scripts/create_dmg.sh`
- Result: success
- Path: `dist/VoidBreaker.dmg`
- Size: `50M`
- Tool path used: `hdiutil` fallback (`create-dmg` not installed)

### DMG mount and contents

- Command: `hdiutil attach dist/VoidBreaker.dmg -nobrowse -quiet`
- Result: mounted successfully at `/Volumes/VoidBreaker`
- Verified entries:
  - `VoidBreaker.app`
  - `Applications -> /Applications` symlink

### Install and launch smoke test

- Installed with copy flow equivalent to drag-to-install:
  - `cp -R /Volumes/VoidBreaker/VoidBreaker.app /Applications/`
- Launch command:
  - `/Applications/VoidBreaker.app/Contents/MacOS/VoidBreaker`
- Result: executable starts successfully

### Persistence behavior check

- Installed app launch in isolated `HOME` did not materialize `settings.json` during a short smoke run (expected when no settings mutation occurs during the run).
- Persistence subsystem round-trip validated using the production `PersistenceManager` with isolated `HOME` and Application Support path:
  - Result: `PERSISTENCE_ROUNDTRIP_OK`

## Definition of Done Status

- [x] `scripts/create_dmg.sh` created and produces a valid DMG
- [x] DMG mounts and contains `VoidBreaker.app` + `Applications` alias/symlink
- [x] Install flow to `/Applications` validated; app launch smoke test passed
- [x] `docs/code-signing-guide.md` added with signing/notarization instructions
- [x] Component overview documentation created
