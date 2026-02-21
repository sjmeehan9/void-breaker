# Phase 6: Packaging & Release — Component Breakdown

Version: 1.0
Date: 2026-02-20
Owner: Tech Lead (Phase 6)

---

## Phase Context

Phase 6 transforms VoidBreaker from a development project into a distributable macOS application. It produces a standalone `.app` bundle via PyInstaller, wraps it in a DMG disk image, validates performance and correctness on a clean system, and creates all release documentation. After this phase, a non-developer user can download a DMG, drag the app to Applications, and play.

**Dependencies from prior phases (do not re-implement):**

- Phase 1 delivered: project skeleton (`pyproject.toml`, directory structure), state machine, persistence layer (`PersistenceManager`, `~/Library/Application Support/VoidBreaker/`), `InputManager`, `AudioManager`, game config system, `platformdirs` storage path resolution
- Phase 2 delivered: `PlayerShip` entity, `EntityManager`, `CombatPhase`, `SpawnManager`, collision system, scoring, level progression, all entity types
- Phase 3 delivered: enemy ships, enemy projectiles, expanded collisions, difficulty scaling for 30+ levels, damage feedback
- Phase 4 delivered: `ShopPhase` with fly-through node interaction, `UpgradeManager`, `InsuranceManager`, `CurrencyManager`, full economy loop
- Phase 5 delivered: all UI screens (main menu, how-to-play, settings, high scores, game over), pause system, complete audio (16 sound effects), particle effects, visual polish, accessibility features (colorblind mode, screen shake), difficulty presets, practice/training mode, all final assets

**Contracts (what this phase exposes):**

- `VoidBreaker.app` — standalone macOS application bundle
- `VoidBreaker.dmg` — distributable disk image
- `README.md` — user-facing installation and gameplay documentation
- `docs/phase-6-summary.md` — final phase summary for project records

---

## Component Summary

| ID | Name | Owner | Effort | Priority | Key Files |
|----|------|-------|--------|----------|-----------|
| 6.1 | Human Setup & Release Preparation | Human | 3h | Must-have | `assets/icon.icns`, source code (string review), `scripts/evals.py` |
| 6.2 | PyInstaller Configuration & Build | AI Agent | 6h | Must-have | `VoidBreaker.spec`, `scripts/build_app.sh` |
| 6.3 | DMG Creation & Distribution Packaging | AI Agent | 4h | Must-have | `scripts/create_dmg.sh`, `docs/code-signing-guide.md` |
| 6.4 | Performance Validation | AI Agent | 4h | Must-have | `scripts/profile_performance.py`, `docs/performance-report.md` |
| 6.5 | Final QA & Cross-Platform Smoke Test | Human + AI Agent | 4h | Must-have | `docs/qa-checklist.md` |
| 6.6 | Release Documentation & E2E Verification | AI Agent | 6h | Must-have | `README.md`, `docs/phase-6-summary.md`, `docs/implementation-context-phase-6.md` |

**File ownership matrix (serialisation constraints):**

| File | Created by | Modified by | Constraint |
|------|-----------|-------------|------------|
| `assets/icon.icns` | 6.1 | 6.2 (referenced) | 6.2 must wait for 6.1 |
| `VoidBreaker.spec` | 6.2 | — | No conflict |
| `scripts/build_app.sh` | 6.2 | — | No conflict |
| `scripts/create_dmg.sh` | 6.3 | — | No conflict |
| `docs/code-signing-guide.md` | 6.3 | — | No conflict |
| `scripts/profile_performance.py` | 6.4 | — | No conflict |
| `docs/performance-report.md` | 6.4 | — | No conflict |
| `docs/qa-checklist.md` | 6.5 | — | No conflict |
| `README.md` | 6.6 | — | No conflict |
| `docs/phase-6-summary.md` | 6.6 | — | No conflict |
| `docs/implementation-context-phase-6.md` | 6.6 | — | No conflict |
| `docs/components/phase-6-component-6-*.md` | 6.6 | — | No conflict |
| Source code (user-facing strings) | Prior phases | 6.1 (string replacement) | 6.1 completes before 6.2 |

**Parallelisation:** Component 6.1 must complete first (human tasks: icon, name finalisation, string review). Components 6.2 depends on 6.1. Component 6.3 depends on 6.2 (needs the built `.app`). Component 6.4 depends on 6.2 (profiles the built `.app`). Components 6.3 and 6.4 can run in parallel after 6.2. Component 6.5 depends on 6.3 (tests the DMG/app). Component 6.6 depends on all prior components.

---

## Components

---

#### Component: 6.1 - Human Setup & Release Preparation

**Priority**: Must-have

**Estimated Effort**: 3 hours

**Owner**: Human

**Dependencies**:
- Phase 5 (5.1): All final assets must be in place (sprites, sounds, fonts)
- Phase 5 (all): Complete, polished game with all UI screens, audio, and visual effects working

**Features**:
- Create `.icns` application icon for macOS — Human
- Finalise product name in all user-facing strings — Human
- Review all placeholder assets and confirm final versions are in place — Human
- Verify no TODO/FIXME comments remain in codebase — Human (run `scripts/evals.py`)
- Confirm licensing compliance (all assets are original) — Human

**Description**:
Isolates all human-only tasks required before the automated build process can begin. The primary deliverables are the macOS application icon (`.icns` format), confirmation that the product name "VoidBreaker" (or the finalised name) appears correctly in all user-facing locations, and verification that no placeholder assets or TODO markers remain. This component gates all subsequent Phase 6 work.

**Acceptance Criteria**:
- [ ] `assets/icon.icns` exists and is a valid macOS icon file containing sizes: 16x16, 32x32, 128x128, 256x256, 512x512 (plus @2x retina variants)
- [ ] The finalised product name appears in: window title (`window.py`), main menu title text, Info.plist bundle name (documented for 6.2), persistence directory name, game over screen, about/credits if present
- [ ] No placeholder sprites remain in `assets/sprites/` — all sprites are final production versions from Phase 5.1
- [ ] No placeholder sounds remain in `assets/sounds/` — all sound effects are final production versions from Phase 5.1
- [ ] `python scripts/evals.py` passes with zero TODO/FIXME findings
- [ ] All public functions have Google-style docstrings (verified by `scripts/evals.py`)
- [ ] No third-party copyrighted assets exist anywhere in `assets/`

**Technical Details**:
- **Files to Create**:
  - `assets/icon.icns`
- **Files to Modify**:
  - `asterax/app/src/window.py` (window title string if not already finalised)
  - `asterax/app/src/states/main_menu.py` (title text if not already finalised)
  - Any other files containing placeholder product name strings
- **Key Functions/Classes**: N/A (asset creation and string review)
- **Human/AI Agent**: All items are Human tasks — icon creation requires design tooling (e.g., macOS `iconutil`, Sketch, Figma, or GIMP), name finalisation requires product decision, asset review requires visual/audio inspection
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: macOS `iconutil` command-line tool (converts `.iconset` folder to `.icns`), or an icon creation tool (e.g., Icon Composer, Figma export, `png2icns`)

**Detailed Implementation Requirements**:
- **File: `assets/icon.icns`**: Create a macOS application icon that represents VoidBreaker's identity — a space-themed design consistent with the retro arcade aesthetic. The `.icns` file must be generated from a `.iconset` folder containing the following PNG files: `icon_16x16.png`, `icon_16x16@2x.png` (32x32), `icon_32x32.png`, `icon_32x32@2x.png` (64x64), `icon_128x128.png`, `icon_128x128@2x.png` (256x256), `icon_256x256.png`, `icon_256x256@2x.png` (512x512), `icon_512x512.png`, `icon_512x512@2x.png` (1024x1024). Use `iconutil -c icns VoidBreaker.iconset` to generate the `.icns` file. The icon should work well at small sizes (dock, Finder sidebar) and large sizes (Finder icon view). Suggested design: a stylised ship silhouette against a dark space background with a subtle glow effect, or a geometric shard/asteroid motif matching the game's retro aesthetic.

- **User-facing string review**: Search the entire `asterax/app/src/` directory for any occurrences of placeholder names or generic titles. The confirmed product name must appear consistently in: `window.py` (the `self.set_caption()` or `title=` argument), `main_menu.py` (the rendered title text), any "About" or credits text, and the persistence directory path (should already be `VoidBreaker` via `platformdirs`). Run: `grep -rn "Asterax\|asterax\|ASTERAX\|placeholder\|PLACEHOLDER\|TODO\|FIXME\|todo\|fixme" asterax/app/src/` and resolve all findings. Note: the project directory name `asterax-tribute` and internal package name `asterax` in imports do NOT need to change — only user-facing strings visible to players matter.

**Test Requirements**:
- [ ] Manual testing: Verify `assets/icon.icns` opens correctly in macOS Preview or Finder's Get Info
- [ ] Manual testing: Launch the game and verify the product name appears correctly in the window title bar
- [ ] Manual testing: Visual inspection of all sprites and sounds — confirm no placeholder/stub assets remain
- [ ] Programmatic testing: `python scripts/evals.py` passes with zero findings

**Definition of Done**:
- [ ] `assets/icon.icns` created and verified
- [ ] Product name finalised in all user-facing strings
- [ ] No placeholder assets remain
- [ ] `scripts/evals.py` passes cleanly
- [ ] Licensing compliance confirmed (written attestation that all assets are original)
- [ ] Documentation created: `docs/components/phase-6-component-6-1-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-6.md` (max 100 lines for this component)

**Notes**:
The `.icns` creation process on macOS is: (1) create a folder named `VoidBreaker.iconset`, (2) place all required PNG sizes inside it with the exact naming convention, (3) run `iconutil -c icns VoidBreaker.iconset`. The output `VoidBreaker.icns` is then renamed/moved to `assets/icon.icns`. If the final product name is NOT "VoidBreaker", update this document and inform the Tech Lead for Phase 6 so that all subsequent components use the correct name in file paths and configurations. The package import name (`asterax`) is internal and does not need to change.

---

#### Component: 6.2 - PyInstaller Configuration & Build

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 6.1: Application icon (`assets/icon.icns`) must exist; product name must be finalised
- Phase 5 (all): Complete game with all assets in `assets/` directory
- Phase 1 (1.2): Entry point is `asterax/app/src/main.py`
- `pyproject.toml`: Package is installable via `pip install -e .`

**Features**:
- Create `VoidBreaker.spec` PyInstaller spec file — AI Agent
- Configure hidden imports for Arcade, pyglet, and OpenGL — AI Agent
- Configure data file mappings for all asset directories — AI Agent
- Configure macOS Info.plist entries — AI Agent
- Create `scripts/build_app.sh` build script — AI Agent
- Build and verify `.app` bundle launches — AI Agent

**Description**:
Creates the PyInstaller configuration that packages VoidBreaker into a standalone macOS `.app` bundle. The spec file must handle all hidden imports required by Arcade and pyglet (which use dynamic module loading), bundle all game assets (sprites, sounds, fonts), configure macOS-specific metadata (Info.plist), and produce a `--onedir` bundle that runs without Python installed on the target machine. A build script automates the full build process.

**Acceptance Criteria**:
- [ ] `VoidBreaker.spec` exists at the project root and is syntactically valid
- [ ] Running `pyinstaller VoidBreaker.spec` produces `dist/VoidBreaker.app/` without errors
- [ ] The built `.app` launches on the build machine and displays the main menu
- [ ] All sprites load correctly from the bundled `.app` (no missing texture errors)
- [ ] All sounds load and play correctly from the bundled `.app` (no missing sound errors)
- [ ] Fonts load correctly from the bundled `.app` (no missing font errors)
- [ ] The window title shows the finalised product name
- [ ] Persistence works: settings and high scores save to `~/Library/Application Support/VoidBreaker/` when launched from the `.app`
- [ ] The `.app` bundle includes a valid `Info.plist` with bundle identifier, version, and minimum OS version
- [ ] No terminal window opens when the `.app` is launched (windowed mode)
- [ ] `scripts/build_app.sh` automates the full build process from a clean state

**Technical Details**:
- **Files to Create**:
  - `VoidBreaker.spec` (project root)
  - `scripts/build_app.sh`
- **Key Functions/Classes**:
  - `VoidBreaker.spec`: PyInstaller spec file with `Analysis`, `PYZ`, `EXE`, `COLLECT`, and `BUNDLE` objects
  - `build_app.sh`: Shell script that activates venv, cleans previous builds, runs PyInstaller, and verifies output
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `pyinstaller` (add to dev dependencies in `pyproject.toml` if not already present — version 6.x), `arcade` 3.x, `pyglet`, `platformdirs`

**Detailed Implementation Requirements**:
- **File: `VoidBreaker.spec`**: The spec file must be a complete PyInstaller configuration, not a minimal auto-generated stub. Key sections:

  **Analysis block**: The entry point is `asterax/app/src/main.py`. The `pathex` should include the project root. `hiddenimports` must include all modules that Arcade and pyglet load dynamically: `['arcade', 'arcade.camera', 'arcade.color', 'arcade.csscolor', 'arcade.resources', 'arcade.text', 'arcade.tilemap', 'pyglet', 'pyglet.gl', 'pyglet.media', 'pyglet.media.codecs', 'pyglet.media.codecs.wave', 'pyglet.media.drivers', 'pyglet.media.drivers.openal', 'pyglet.window', 'pyglet.window.cocoa', 'pyglet.canvas', 'pyglet.canvas.cocoa', 'pyglet.libs', 'pyglet.libs.darwin', 'pyglet.libs.darwin.cocoa', 'pyglet.image', 'pyglet.image.codecs', 'pyglet.image.codecs.png', 'pyglet.font', 'pyglet.font.quartz', 'OpenGL', 'OpenGL.GL', 'OpenGL.platform', 'OpenGL.platform.darwin', 'ctypes', 'ctypes.util', 'json', 'pathlib', 'dataclasses', 'enum', 'math', 'random', 'time', 'logging', 'platformdirs']`. This list may need expansion during testing — hidden import errors manifest as `ModuleNotFoundError` at runtime. The `datas` field maps asset directories into the bundle: `[('asterax/assets/sprites', 'assets/sprites'), ('asterax/assets/sounds', 'assets/sounds'), ('asterax/assets/fonts', 'assets/fonts'), ('assets/icon.icns', '.')]`. Note: the exact source paths depend on the project's asset directory structure — verify the actual paths before writing the spec. `excludes` should include modules not needed at runtime to reduce bundle size: `['tkinter', 'unittest', 'test', 'distutils', 'setuptools', 'pip', 'wheel', 'pytest', 'black', 'isort', 'mypy']`.

  **PYZ, EXE, COLLECT blocks**: Standard PyInstaller configuration. The `EXE` name should be `'VoidBreaker'`. Set `console=False` for windowed mode (no terminal). Set `icon='assets/icon.icns'`.

  **BUNDLE block** (macOS-specific): This wraps the `COLLECT` output into a `.app` bundle. Configure `bundle_identifier='com.voidbreaker.game'`, `info_plist` dictionary with: `'CFBundleName': 'VoidBreaker'`, `'CFBundleDisplayName': 'VoidBreaker'`, `'CFBundleVersion': '1.0.0'`, `'CFBundleShortVersionString': '1.0.0'`, `'LSMinimumSystemVersion': '13.0'`, `'NSHighResolutionCapable': True`, `'CFBundleIconFile': 'icon.icns'`. The `icon` parameter should point to `'assets/icon.icns'`.

  **Asset path resolution**: The bundled application must resolve asset paths correctly at runtime. PyInstaller sets `sys._MEIPASS` as the base directory when running from a bundle. The game's asset loading code (likely in `game_config.py` or a resource utility) must detect whether it's running from source or from a PyInstaller bundle and resolve paths accordingly. If this detection does not already exist, create a utility function:
  ```python
  import sys
  from pathlib import Path

  def get_asset_path() -> Path:
      """Return the base path for game assets."""
      if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
          return Path(sys._MEIPASS) / 'assets'
      return Path(__file__).resolve().parent.parent.parent / 'assets'
  ```
  This function should be placed in `asterax/app/src/config/game_config.py` or a new `asterax/app/src/utils/paths.py` file. All asset loading throughout the codebase must use this function rather than hardcoded relative paths. If the existing code already uses a centralised asset path, modify it to include the `sys._MEIPASS` detection.

- **File: `scripts/build_app.sh`**: A shell script that automates the build process. Steps: (1) Activate the virtual environment: `source .venv/bin/activate`. (2) Verify PyInstaller is installed: `pip show pyinstaller || pip install pyinstaller`. (3) Clean previous builds: `rm -rf build/ dist/`. (4) Run PyInstaller: `pyinstaller VoidBreaker.spec --noconfirm`. (5) Verify the output exists: check that `dist/VoidBreaker.app/Contents/MacOS/VoidBreaker` is an executable. (6) Print the bundle size: `du -sh dist/VoidBreaker.app`. (7) Print success message with path. The script should `set -e` to fail fast on any error. Make the script executable: `chmod +x scripts/build_app.sh`.

**Test Requirements**:
- [ ] Build verification: `pyinstaller VoidBreaker.spec` completes without errors
- [ ] Launch verification: `open dist/VoidBreaker.app` or `dist/VoidBreaker.app/Contents/MacOS/VoidBreaker` launches the game
- [ ] Asset verification: Game launches and main menu renders (sprites load), navigating to combat shows ship/asteroids (sprites load), audio plays on game events (sounds load)
- [ ] Persistence verification: Change a setting in the bundled app, quit, relaunch, verify setting persisted to `~/Library/Application Support/VoidBreaker/settings.json`
- [ ] No-terminal verification: Launching via Finder double-click does not open a Terminal window
- [ ] Manual testing: Run `scripts/build_app.sh` from a clean state and verify it produces a working `.app`

**Definition of Done**:
- [ ] `VoidBreaker.spec` created and produces a working `.app` bundle
- [ ] `scripts/build_app.sh` automates the build process
- [ ] Built `.app` launches, renders correctly, plays audio, and persists data
- [ ] No terminal window appears on launch
- [ ] Documentation created: `docs/components/phase-6-component-6-2-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-6.md` (max 100 lines for this component)
- [ ] No regression in source-mode execution (`python -m asterax.app.src.main` still works)

**Notes**:
Hidden import debugging is the most common PyInstaller issue. If the `.app` launches but crashes immediately, run it from the terminal (`dist/VoidBreaker.app/Contents/MacOS/VoidBreaker`) to see the traceback. `ModuleNotFoundError` means a hidden import is missing — add it to the `hiddenimports` list and rebuild. Asset loading failures (`FileNotFoundError`) mean the `datas` mapping is incorrect or the asset path resolution does not detect `sys._MEIPASS`. Test the asset path utility function independently before running the full build. The `--onedir` mode (vs `--onefile`) is chosen because it produces a standard `.app` bundle structure and is easier to debug — individual files in `_internal/` can be inspected. Bundle size is expected to be 100-300MB due to bundled Python interpreter, Arcade, pyglet, and OpenGL libraries.

---

#### Component: 6.3 - DMG Creation & Distribution Packaging

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 6.2: Built `VoidBreaker.app` must exist at `dist/VoidBreaker.app`

**Features**:
- Create DMG disk image with VoidBreaker.app and Applications alias — AI Agent
- Configure DMG background and layout — AI Agent
- Create `scripts/create_dmg.sh` automation script — AI Agent
- Document code signing and notarisation steps for future releases — AI Agent

**Description**:
Creates a distributable DMG disk image that provides the standard macOS drag-to-install experience. The DMG contains VoidBreaker.app and a symbolic link to `/Applications`, allowing users to drag the app into their Applications folder. A background image and window layout provide a polished installation experience. Code signing and notarisation are documented for future releases but are not required for v1.0 local distribution.

**Acceptance Criteria**:
- [ ] `scripts/create_dmg.sh` produces a DMG file at `dist/VoidBreaker.dmg`
- [ ] The DMG mounts in Finder and shows VoidBreaker.app and an "Applications" alias
- [ ] Dragging VoidBreaker.app to the Applications alias installs the app correctly
- [ ] The installed app launches from `/Applications/VoidBreaker.app` without errors
- [ ] Persistence works from the installed location (settings/high scores save correctly)
- [ ] `docs/code-signing-guide.md` documents the codesign and notarytool process for future releases
- [ ] The DMG file size is documented (expected: 100-300MB)

**Technical Details**:
- **Files to Create**:
  - `scripts/create_dmg.sh`
  - `docs/code-signing-guide.md`
- **Key Functions/Classes**:
  - `create_dmg.sh`: Shell script using `hdiutil` to create the DMG
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: macOS `hdiutil` (system command, always available on macOS), optionally `create-dmg` (installable via `brew install create-dmg` for prettier DMG layout)

**Detailed Implementation Requirements**:
- **File: `scripts/create_dmg.sh`**: The script creates a DMG disk image using macOS `hdiutil`. Two approaches are supported — the script should try `create-dmg` first (if installed) for a polished result, and fall back to raw `hdiutil` if it is not available.

  **Option A — `create-dmg` (preferred if available)**:
  ```bash
  create-dmg \
    --volname "VoidBreaker" \
    --volicon "assets/icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "VoidBreaker.app" 150 200 \
    --app-drop-link 450 200 \
    --no-internet-enable \
    "dist/VoidBreaker.dmg" \
    "dist/VoidBreaker.app"
  ```

  **Option B — raw `hdiutil` fallback**: (1) Create a temporary directory: `tmp_dmg=$(mktemp -d)`. (2) Copy the `.app` into it: `cp -R dist/VoidBreaker.app "$tmp_dmg/"`. (3) Create the Applications symlink: `ln -s /Applications "$tmp_dmg/Applications"`. (4) Create the DMG: `hdiutil create -volname "VoidBreaker" -srcfolder "$tmp_dmg" -ov -format UDZO "dist/VoidBreaker.dmg"`. (5) Clean up the temp directory: `rm -rf "$tmp_dmg"`. (6) Verify the DMG: `hdiutil verify dist/VoidBreaker.dmg`.

  The script should: `set -e` for fail-fast, check that `dist/VoidBreaker.app` exists before proceeding, print the final DMG file size, and print a success message. Make the script executable: `chmod +x scripts/create_dmg.sh`.

- **File: `docs/code-signing-guide.md`**: Document the following steps for future releases (not executed for v1.0):

  **Code signing** (required for distribution outside the Mac App Store without Gatekeeper warnings):
  ```bash
  codesign --force --deep --sign "Developer ID Application: <TEAM_NAME> (<TEAM_ID>)" \
    --options runtime \
    --entitlements entitlements.plist \
    dist/VoidBreaker.app
  ```
  Document that an Apple Developer account ($99/year) is required, and a "Developer ID Application" certificate must be generated from the Apple Developer portal. An `entitlements.plist` may be needed for OpenGL/OpenAL usage.

  **Notarisation** (required for macOS Ventura+ to avoid "unidentified developer" warning):
  ```bash
  ditto -c -k --keepParent dist/VoidBreaker.app dist/VoidBreaker.zip
  xcrun notarytool submit dist/VoidBreaker.zip \
    --apple-id "<APPLE_ID>" \
    --team-id "<TEAM_ID>" \
    --password "<APP_SPECIFIC_PASSWORD>" \
    --wait
  xcrun stapler staple dist/VoidBreaker.app
  ```
  Document that notarisation requires an app-specific password generated from appleid.apple.com, and the `--wait` flag blocks until Apple's servers complete the scan (typically 5-15 minutes).

  **Unsigned distribution workaround** (for v1.0): Document that users installing the unsigned `.app` will need to: right-click the app -> "Open" -> confirm the security dialog, OR go to System Preferences -> Privacy & Security -> click "Open Anyway" after the first blocked launch attempt.

**Test Requirements**:
- [ ] Build verification: `scripts/create_dmg.sh` completes without errors
- [ ] Mount verification: `hdiutil attach dist/VoidBreaker.dmg` mounts successfully
- [ ] Content verification: Mounted DMG contains `VoidBreaker.app` and `Applications` alias
- [ ] Install verification: Drag VoidBreaker.app to Applications (or `cp -R`), launch from `/Applications/`, verify game works
- [ ] Manual testing: Open the DMG on a separate macOS user account (if available) to verify no build-machine-specific path dependencies
- [ ] Cleanup verification: `hdiutil detach /Volumes/VoidBreaker` unmounts cleanly

**Definition of Done**:
- [ ] `scripts/create_dmg.sh` created and produces a valid DMG
- [ ] DMG mounts, contains app and Applications alias, drag-to-install works
- [ ] Installed app launches and functions correctly from `/Applications/`
- [ ] `docs/code-signing-guide.md` documents signing and notarisation steps
- [ ] Documentation created: `docs/components/phase-6-component-6-3-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-6.md` (max 100 lines for this component)

**Notes**:
The `create-dmg` tool produces a more polished DMG with configurable window layout and icon positioning. If it is not installed, the `hdiutil` fallback produces a functional but plainer DMG. For v1.0, either is acceptable. The DMG format `UDZO` (zlib-compressed) provides good compression. If the DMG exceeds 500MB, consider using `UDBZ` (bzip2) for better compression. The unsigned `.app` will trigger macOS Gatekeeper on first launch — the code signing guide documents the workaround for end users and the proper signing process for future releases.

---

#### Component: 6.4 - Performance Validation

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: AI Agent

**Dependencies**:
- 6.2: Built `VoidBreaker.app` must exist for profiling the packaged application
- Phase 3 (3.6): Difficulty tables define the entity counts at various levels
- Phase 2 (2.7): Combat phase manages entity spawning and the game loop

**Features**:
- Create performance profiling script — AI Agent
- Profile at peak entity count (100 asteroids, 10 enemies, 15 player projectiles, 20 enemy projectiles, 40 pickups, 300 particles) — AI Agent
- Verify stable 60fps at peak load — AI Agent
- Test for memory leaks over 30+ minutes — AI Agent
- Document performance characteristics — AI Agent

**Description**:
Validates that VoidBreaker meets its performance targets when running as a packaged `.app` bundle. The primary target is stable 60fps (16.67ms per frame) at peak entity count as defined in the solution design. Memory stability is verified over a 30+ minute session to ensure no monotonic memory growth. Results are documented in a performance report.

**Acceptance Criteria**:
- [ ] `scripts/profile_performance.py` exists and can be run to profile the game
- [ ] At peak entity count (100 asteroids, 10 enemies, 15 player projectiles, 20 enemy projectiles, 40 pickups, 300 particles), average frame time is under 16.67ms
- [ ] No individual frame exceeds 33ms (allows occasional frame budget overshoot without dropping below 30fps)
- [ ] Memory usage does not grow monotonically over a 30-minute session (no leaks)
- [ ] Memory usage at steady state is documented
- [ ] Performance characteristics are documented in `docs/performance-report.md`
- [ ] Testing covers both source-mode (`python -m asterax.app.src.main`) and packaged-mode (`VoidBreaker.app`)

**Technical Details**:
- **Files to Create**:
  - `scripts/profile_performance.py`
  - `docs/performance-report.md`
- **Key Functions/Classes**:
  - `profile_performance.py`: Script that launches the game in a stress-test mode, spawns peak entities, measures frame times, and logs memory usage
  - Performance report: Markdown document with frame time statistics and memory graphs
- **Human/AI Agent**: All features are AI Agent tasks
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `psutil` (for memory monitoring — add to dev dependencies if not present), `cProfile` or `time.perf_counter_ns` (stdlib), Arcade's built-in FPS counter (`arcade.get_fps()`)

**Detailed Implementation Requirements**:
- **File: `scripts/profile_performance.py`**: This script automates performance measurement. It should be runnable independently (not as part of the game). Two modes of operation:

  **Mode 1 — Integrated stress test (preferred)**: Import the game's entity manager and combat state. Create a headless-like test environment (or a visible window with automated input) that spawns the peak entity count simultaneously: 100 asteroids (mixed sizes), 10 enemy ships, 15 player projectiles, 20 enemy projectiles, 40 currency pickups, and 300 active particles. Run the game loop for a configurable duration (default: 60 seconds) while recording frame times. After the test, print statistics: min/max/mean/median/p95/p99 frame times, FPS statistics, and total frame count.

  **Mode 2 — External monitoring (fallback)**: If headless stress testing is not feasible with Arcade (Arcade requires an OpenGL context), create a script that: (1) launches the game process, (2) monitors its memory usage via `psutil.Process.memory_info()` at 1-second intervals for a configurable duration, (3) outputs a CSV of timestamp/RSS/VMS readings, (4) prints summary statistics (initial memory, peak memory, final memory, growth trend).

  The script should also leverage Arcade's built-in performance tools if available. `arcade.get_fps()` returns the current FPS and can be logged per frame. If the game has a debug overlay or an FPS counter (common in Arcade games), enable it during profiling.

  For the 30-minute memory leak test: the script should either run Mode 2 for 30+ minutes or instrument the game to log memory usage at 1-minute intervals during a normal play session. The output should show whether RSS memory grows monotonically (leak) or stabilises (no leak). A linear regression on the memory samples with a positive slope exceeding 1MB/minute should be flagged as a potential leak.

- **File: `docs/performance-report.md`**: Structure:
  - **Test Environment**: macOS version, hardware (CPU, GPU, RAM), Python version, Arcade version
  - **Frame Time Results**: Table with entity count, mean frame time, p95, p99, min FPS, target met (yes/no)
  - **Memory Results**: Initial RSS, peak RSS, final RSS, 30-min growth, leak detected (yes/no)
  - **Bottleneck Analysis**: If any targets are missed, identify the subsystem consuming the most time (physics, collision, rendering, particles) using `cProfile` output
  - **Recommendations**: Any optimisation suggestions if targets are not met
  - **Conclusion**: Pass/fail summary

**Test Requirements**:
- [ ] `scripts/profile_performance.py` runs without errors in source mode
- [ ] Frame time statistics are printed to stdout
- [ ] Memory monitoring produces readable output (CSV or tabular)
- [ ] Manual testing: Play the packaged `.app` for 30+ minutes and observe memory usage in Activity Monitor — verify no continuous growth
- [ ] Programmatic testing: Run the profiling script and verify that frame times meet the 16.67ms target

**Definition of Done**:
- [ ] `scripts/profile_performance.py` created and functional
- [ ] Performance profiled at peak entity count — results documented
- [ ] Memory stability verified over 30+ minutes — results documented
- [ ] `docs/performance-report.md` created with full results
- [ ] All performance targets met (60fps at peak load, no memory leaks)
- [ ] Documentation created: `docs/components/phase-6-component-6-4-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-6.md` (max 100 lines for this component)

**Notes**:
Arcade requires an OpenGL context for rendering, so truly headless profiling may not be possible. The stress test may need to run with a visible window. If running on a CI machine without a GPU, skip the profiling and document that it must be run manually on a macOS machine with a GPU. The performance targets from the solution design are conservative — Arcade can handle 8000+ sprites, and VoidBreaker peaks at ~500 total entities. The primary risk is particle system overhead or collision detection with many asteroids. If profiling reveals a bottleneck, document the finding but do NOT optimise within Phase 6 unless the game drops below 30fps — optimisation would be a separate task.

---

#### Component: 6.5 - Final QA & Cross-Platform Smoke Test

**Priority**: Must-have

**Estimated Effort**: 4 hours

**Owner**: Human + AI Agent

**Dependencies**:
- 6.3: DMG must be created for install-from-DMG testing
- 6.2: Built `.app` must exist for direct launch testing
- Phase 5 (all): All game features must be complete

**Features**:
- Full playthrough of packaged `.app` on clean macOS — Human
- Verify all game systems in packaged app (combat, shop, insurance, persistence, audio, UI) — Human
- Create and execute structured QA checklist — AI Agent
- Optional Windows/Linux smoke test via PyInstaller cross-build — Human (if platform available)
- Document known issues — AI Agent

**Description**:
Provides comprehensive final quality assurance for the packaged VoidBreaker application. A structured checklist covers every game system, tested from the user's perspective using the packaged `.app` (not the development source). The goal is to catch any packaging-specific issues: missing assets, broken paths, performance regressions, persistence failures, or UI/UX problems that only manifest in the bundled application. Ideally tested on a clean macOS install (separate user account or clean VM) with no Python development tools installed.

**Acceptance Criteria**:
- [ ] Full game loop completed in packaged `.app`: launch -> main menu -> new game -> play 5+ levels -> use shop each level -> die -> game over summary -> high score entry -> verify on leaderboard -> restart
- [ ] All game systems verified in packaged app: combat (ship, asteroids, enemies, projectiles), shop (fly-through purchase, re-centring, continue), insurance (purchase, cost deduction, retention on death), persistence (settings save/load, high scores save/load), audio (all 16 sound effects play), visual effects (particles, screen shake, damage flash), accessibility (colorblind mode toggle, screen shake settings), difficulty presets (casual/classic/hard produce different experiences)
- [ ] Practice/Training mode launches and works in packaged app
- [ ] Pause system works in packaged app (freeze/resume, restart, exit to menu)
- [ ] `docs/qa-checklist.md` documents all test cases and their pass/fail status
- [ ] Any known issues are documented with severity and workaround

**Technical Details**:
- **Files to Create**:
  - `docs/qa-checklist.md`
- **Key Functions/Classes**: N/A (manual testing with structured checklist)
- **Human/AI Agent**:
  - Create QA checklist document — AI Agent
  - Execute QA checklist on packaged `.app` — Human
  - Document results and known issues — AI Agent (from human's findings)
  - Optional cross-platform smoke test — Human (requires Windows/Linux machine)
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: A macOS 13+ machine (ideally a separate user account or VM without development tools installed)

**Detailed Implementation Requirements**:
- **File: `docs/qa-checklist.md`**: A structured checklist covering every testable game feature, organised by system. Each item has a pass/fail status, notes field, and severity rating (P0-blocker, P1-critical, P2-major, P3-minor, P4-cosmetic). The checklist should cover the following categories:

  **1. Installation & Launch**: DMG mounts correctly, drag-to-install works, app launches from `/Applications/`, no terminal window appears, window title is correct, Gatekeeper workaround documented (right-click -> Open).

  **2. Main Menu**: All menu items visible and navigable (New Game, How to Play, Settings, High Scores, Quit), keyboard navigation works, menu sounds play on navigate/select.

  **3. Settings**: Key remapping works, volume controls work (master, music, SFX), colorblind mode toggles, screen shake settings apply, difficulty preset changes, fire mode toggle, settings persist across app restart.

  **4. Combat**: Ship responds to controls (thrust, rotation, fire, brake), inertial physics feel correct, asteroids spawn and split correctly (large->medium->small), asteroids/ship/projectiles wrap at screen edges, currency drops from destroyed asteroids, enemy ships appear at configured levels, enemy projectiles damage player, player projectiles destroy enemies, damage feedback (flash, sound, invulnerability), HUD displays correct values (shields, score, level, currency).

  **5. Shop**: Shop activates after level clear, nodes arranged in circle, ship controls work in shop, fly-into-node purchases upgrade, currency deducted correctly, denied sound on insufficient funds, ship re-centres after purchase, "Continue" node returns to combat, upgrade effects visible in next combat level.

  **6. Insurance**: Insurance purchasable in shop, cost deducted each level, premium retains all upgrades on death, basic retains ~50%, off retains nothing.

  **7. Game Over & High Scores**: Game over triggers when shields reach zero, run summary displays accurate stats, high score entry works (initials input), high score persists across restarts, leaderboard displays correctly.

  **8. Audio**: All 16 sound effects play on correct events (fire, hit, explosion x3, enemy explosion, pickup currency, pickup buff, shop purchase, shop denied, level clear, game over, menu navigate, menu select, plus any additional).

  **9. Visual Effects**: Explosion particles render (3 sizes), thrust trail visible, pickup sparkle on collection, damage flash on hit, screen shake on damage (if enabled), level transition effect.

  **10. Practice Mode**: Accessible from main menu, toggles work (asteroids only, infinite shields), no high score recording, return to menu works.

  **11. Pause**: Pause triggers on Escape, all action freezes, resume restores state, restart works, exit to menu works.

  **12. Performance**: No noticeable frame drops during normal play, no frame drops during intense combat (20+ entities), no lag on input.

  **13. Cross-Platform (Optional)**: If tested on Windows — app launches, basic gameplay works, persistence works. If tested on Linux — same checks.

**Test Requirements**:
- [ ] Manual testing: Complete the full QA checklist on the packaged `.app`
- [ ] Manual testing: Test on a clean macOS user account (no Python, no dev tools) if possible
- [ ] Manual testing: Verify Gatekeeper workaround works for unsigned app
- [ ] Optional: Smoke test on Windows or Linux

**Definition of Done**:
- [ ] `docs/qa-checklist.md` created with all test cases
- [ ] QA checklist executed — all P0 and P1 items pass
- [ ] Any P2+ issues documented with severity and workaround
- [ ] No P0 (blocker) issues remain open
- [ ] Documentation created: `docs/components/phase-6-component-6-5-overview.md`
- [ ] Documentation updated: `docs/implementation-context-phase-6.md` (max 100 lines for this component)

**Notes**:
Testing on a completely clean macOS install is the gold standard for catching packaging issues. If a separate machine or VM is not available, create a new macOS user account on the build machine (System Preferences -> Users & Groups) and test from that account. This verifies that no development-machine-specific paths or environment variables are required. The most common packaging failures are: missing assets (file paths wrong in spec), missing hidden imports (dynamic pyglet/Arcade modules), and persistence path issues (hardcoded paths vs `platformdirs` resolution). Cross-platform testing (Windows/Linux) is optional for v1.0 and should not block the release.

---

#### Component: 6.6 - Release Documentation & E2E Verification

**Priority**: Must-have

**Estimated Effort**: 6 hours

**Owner**: AI Agent

**Dependencies**:
- 6.1, 6.2, 6.3, 6.4, 6.5: All prior Phase 6 components must be complete
- Phase 5 (all): All game features implemented and tested

**Features**:
- Create `README.md` with installation, requirements, controls, and gameplay overview — AI Agent
- Run final `scripts/evals.py` and verify clean pass — AI Agent
- Run final `pytest` suite and verify all tests pass — AI Agent
- Create `docs/phase-6-summary.md` — AI Agent
- Create component overview documents for all Phase 6 components — AI Agent
- Update `docs/implementation-context-phase-6.md` — AI Agent
- Tag release in version control — AI Agent

**Description**:
Creates all release-facing and project documentation, runs final verification of the complete codebase, and tags the release. The README is the primary user-facing document — it tells a non-developer how to install and play VoidBreaker. The phase summary captures what was delivered, decisions made, and known issues. This is the final component of the final phase.

**Acceptance Criteria**:
- [ ] `README.md` exists at the project root with: installation instructions (DMG drag-to-install), system requirements (macOS 13+, Apple Silicon or Intel), controls reference (all default key bindings), gameplay overview (combat, shop, insurance, scoring), known issues (if any), credits
- [ ] `python scripts/evals.py` passes with zero findings (no TODO/FIXME, all docstrings present)
- [ ] `pytest -q --cov=asterax/app/src --cov-report=term-missing` passes with 30%+ coverage
- [ ] `black --check asterax/app/src/` passes
- [ ] `isort --check-only asterax/app/src/` passes
- [ ] `docs/phase-6-summary.md` created with phase deliverables, decisions, and known issues
- [ ] All component overview documents created: `docs/components/phase-6-component-6-1-overview.md` through `phase-6-component-6-6-overview.md`
- [ ] `docs/implementation-context-phase-6.md` created with all component summaries (max 600 lines total)
- [ ] Release tagged in version control (e.g., `v1.0.0`)

**Technical Details**:
- **Files to Create**:
  - `README.md` (project root)
  - `docs/phase-6-summary.md`
  - `docs/implementation-context-phase-6.md`
  - `docs/components/phase-6-component-6-1-overview.md`
  - `docs/components/phase-6-component-6-2-overview.md`
  - `docs/components/phase-6-component-6-3-overview.md`
  - `docs/components/phase-6-component-6-4-overview.md`
  - `docs/components/phase-6-component-6-5-overview.md`
  - `docs/components/phase-6-component-6-6-overview.md`
- **Key Functions/Classes**: N/A (documentation and verification)
- **Human/AI Agent**: All features are AI Agent tasks. The version control tag may require human approval if branch protection is configured.
- **Database Changes**: None
- **API Endpoints**: None
- **Dependencies**: `pytest`, `pytest-cov`, `black`, `isort`, `git`

**Detailed Implementation Requirements**:
- **File: `README.md`**: The README is the first thing a user sees. Structure:

  **Header**: Product name, one-line description ("A retro arcade space shooter inspired by classic Mac shareware games"), and a screenshot or logo (if available — reference `assets/icon.icns` as a fallback).

  **Installation**: Step-by-step for macOS: (1) Download `VoidBreaker.dmg` from [release location]. (2) Open the DMG file. (3) Drag `VoidBreaker.app` to your Applications folder. (4) Launch VoidBreaker from Applications. (5) If macOS blocks the app (unsigned): right-click the app, select "Open", confirm the dialog. Note: First launch may take a few seconds as macOS verifies the app.

  **System Requirements**: macOS 13 (Ventura) or later. Apple Silicon (M1/M2/M3/M4) or Intel x86_64. 512MB available disk space. OpenGL 3.3+ capable GPU (all Macs since 2012).

  **Controls**: Table of default key bindings: Arrow Left — Rotate Left, Arrow Right — Rotate Right, Arrow Up — Thrust, Arrow Down — Brake, Space — Fire, Escape — Pause, Enter — Confirm/Continue. Note: controls are remappable in Settings.

  **How to Play**: Brief gameplay overview covering: (1) Combat — destroy asteroids and enemies, collect currency crystals. (2) Shop — between levels, fly your ship into upgrade nodes to purchase improvements. (3) Upgrades — improve weapons, defense, mobility, and economy. (4) Insurance — protect your upgrades against death (costs currency each level). (5) Scoring — points for destroying asteroids (by size) and enemies. High scores are saved locally.

  **Game Modes**: Classic Endless (default — survive as long as possible), Practice/Training (learn controls with reduced difficulty).

  **Building from Source** (for developers): Prerequisites (Python 3.13+, macOS), clone, `pip install -e .`, `python -m asterax.app.src.main`. Building the `.app`: `scripts/build_app.sh`. Creating the DMG: `scripts/create_dmg.sh`.

  **Known Issues**: List any issues discovered during QA (from `docs/qa-checklist.md`).

  **Credits**: Developed by [team/individual]. Built with Python and the Arcade library.

  **License**: [As appropriate — specify the project's license].

- **File: `docs/phase-6-summary.md`**: Structure: Phase overview, components delivered, key decisions made (PyInstaller configuration choices, DMG format, asset path resolution approach, performance results), known issues and their severity, metrics (bundle size, peak FPS, memory usage, test coverage), and recommendations for future releases (code signing, notarisation, cross-platform builds).

- **File: `docs/implementation-context-phase-6.md`**: Running log of implemented components, maximum 100 lines per component (600 lines total for 6 components). Each entry summarises: what was built, key files created/modified, patterns established, integration points, and any deviations from the component breakdown spec.

- **Version control tag**: After all documentation is complete and all checks pass, tag the release:
  ```bash
  git tag -a v1.0.0 -m "VoidBreaker v1.0.0 — Initial release"
  ```
  Do NOT push the tag without human approval. The tag marks the exact commit that produced the release `.app` and DMG.

**Test Requirements**:
- [ ] `python scripts/evals.py` passes with zero findings
- [ ] `pytest -q --cov=asterax/app/src --cov-report=term-missing` passes with 30%+ coverage
- [ ] `black --check asterax/app/src/` passes
- [ ] `isort --check-only asterax/app/src/` passes
- [ ] Manual review: `README.md` is accurate, complete, and free of typos
- [ ] Manual review: All component overview documents exist in `docs/components/`
- [ ] Manual review: `docs/phase-6-summary.md` accurately reflects what was delivered

**Definition of Done**:
- [ ] `README.md` created with complete user documentation
- [ ] All quality checks pass (`evals.py`, `pytest`, `black`, `isort`)
- [ ] `docs/phase-6-summary.md` created
- [ ] All 6 component overview documents created in `docs/components/`
- [ ] `docs/implementation-context-phase-6.md` created
- [ ] Release tagged as `v1.0.0` in version control (pending human approval to push)
- [ ] Core application still launches and full game loop works
- [ ] No TODO/FIXME comments remain in any delivered file

**Notes**:
The README should be concise and user-focused — developers can read the `docs/` directory for technical details. Avoid technical jargon in the installation and gameplay sections. The version tag `v1.0.0` follows semantic versioning: 1 (first major release), 0 (no minor updates), 0 (no patches). Future releases increment accordingly. If the project is not using git yet, initialise it before tagging (`git init && git add . && git commit -m "Initial commit"`). The tag should only be created after ALL Phase 6 components pass their acceptance criteria.

---

## Dependency Graph

```
6.1 (Human Setup)
 |
 +---> 6.2 (PyInstaller Build)
        |
        +---> 6.3 (DMG Creation)
        |       |
        |       +---> 6.5 (Final QA)
        |                |
        +---> 6.4 (Performance) ---> 6.5
                                      |
                                      +---> 6.6 (Release Docs & E2E)
```

**Parallelisable groups after 6.1:**
- Sequential: 6.1 -> 6.2
- Parallel after 6.2: 6.3 and 6.4
- Sequential after 6.3 + 6.4: 6.5 -> 6.6

---

## Release Checklist Summary

Before considering Phase 6 complete, verify every item:

1. **Icon**: `assets/icon.icns` exists and renders correctly in Finder
2. **Name**: Product name is consistent across window title, menus, Info.plist, persistence path
3. **Code quality**: `evals.py` passes, no TODO/FIXME, all docstrings present
4. **Build**: `VoidBreaker.spec` produces a working `.app` via `scripts/build_app.sh`
5. **Bundle**: `.app` launches, renders, plays audio, persists data, no terminal window
6. **DMG**: `VoidBreaker.dmg` mounts, drag-to-install works, installed app runs
7. **Performance**: 60fps at peak entity count, no memory leaks over 30 minutes
8. **QA**: Full game loop verified in packaged app, all systems functional
9. **Docs**: README.md, phase-6-summary.md, all component overviews, implementation context
10. **Tag**: `v1.0.0` tag created in version control
