# Phase 6 Component 6.2 — PyInstaller Configuration & Build

## Summary

Component 6.2 is complete. A production PyInstaller spec and automated build script now generate a standalone macOS app bundle at `dist/VoidBreaker.app`, with bundled assets, macOS metadata, windowed mode, and reproducible build steps.

## Deliverables Completed

- Created `VoidBreaker.spec` at project root.
- Created executable build script `scripts/build_app.sh`.
- Added PyInstaller dev dependency in `pyproject.toml` (`pyinstaller>=6.0`).
- Added runtime bundle-aware asset path utility:
  - `app/src/utils/paths.py`
  - `app/src/utils/__init__.py`
- Refactored asset path resolution to support source + bundled runtimes:
  - `app/src/config/game_config.py`
  - `app/src/config/enemy_config.py`
  - `app/src/entities/projectile.py`
  - `app/src/entities/pickups.py`
  - `app/src/rendering/particle_system.py`
  - `app/src/states/combat.py`
  - `app/src/states/shop.py`
  - `app/src/window.py`

## PyInstaller Configuration Notes

### Spec configuration

- Entry point: `app/src/main.py`
- App name: `VoidBreaker`
- Bundle type: macOS `.app` via `BUNDLE`
- Mode: windowed (`console=False`)
- Icon: `assets/icon.icns`
- Data mappings:
  - `assets/sprites -> assets/sprites`
  - `assets/sounds -> assets/sounds`
  - `assets/fonts -> assets/fonts`
  - `assets/icon.icns -> .`
- Info.plist metadata:
  - `CFBundleName`, `CFBundleDisplayName`: `VoidBreaker`
  - `CFBundleVersion`, `CFBundleShortVersionString`: `1.0.0`
  - `LSMinimumSystemVersion`: `13.0`
  - `NSHighResolutionCapable`: `True`
  - `CFBundleIconFile`: `icon.icns`
- Hidden imports are filtered at spec runtime to include only available modules in the current environment, preventing build-time hard failures on version-specific module layouts.

### Build script behavior

`./scripts/build_app.sh` performs:
1. venv activation
2. PyInstaller availability check/install
3. clean build directories (`build/`, `dist/`)
4. app build (`pyinstaller VoidBreaker.spec --noconfirm`)
5. post-build Arcade `VERSION` normalization fix
6. executable existence check
7. bundle size reporting

## Validation Runbook and Results

### Build verification

- Command: `source .venv/bin/activate && ./scripts/build_app.sh`
- Result: success
- Output app: `dist/VoidBreaker.app`
- Bundle size: `108M`

### Launch verification

- Command: `dist/VoidBreaker.app/Contents/MacOS/VoidBreaker`
- Result: executable starts without the prior `arcade/VERSION` runtime crash.

### Source-mode regression verification

- Command: `python -c "from asterax.app.src.main import main; print('import-ok')"`
- Result: `import-ok`

### Focused test regression

- Command: `pytest -q tests/test_config.py tests/test_audio_rendering.py tests/test_main.py`
- Result: `18 passed`

## Known Build Notes

- PyInstaller may emit non-fatal platform library warnings (`libc.so.6`, `winmm`, `ole32`, `shell32`) during macOS builds due to transitive optional dependencies from cross-platform stacks. These warnings do not block bundle generation.
- A deterministic post-build normalization step is included for the Arcade `VERSION` artifact to prevent runtime failure in this environment.

## Definition of Done Status

- [x] `VoidBreaker.spec` created and produces a working `.app` bundle
- [x] `scripts/build_app.sh` automates the build process
- [x] Built `.app` launches and no terminal is required (`console=False`)
- [x] No regression in source-mode execution import path
- [x] Documentation updated for component 6.2
