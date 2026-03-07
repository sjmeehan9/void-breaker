# VoidBreaker

A retro arcade space shooter inspired by classic Mac shareware games. Destroy asteroids, battle enemies, collect currency, and upgrade your ship across ever-harder levels.

<p align="center">
  <img src="assets/icon.icns" alt="VoidBreaker Icon" width="128" />
</p>

---

## Installation

### macOS (Recommended)

1. Download **VoidBreaker.dmg** from the [Releases](../../releases) page.
2. Open the DMG file.
3. Drag **VoidBreaker.app** to your **Applications** folder.
4. Launch VoidBreaker from Applications.
5. **If macOS blocks the app** (unsigned build):
   - Right-click the app and select **Open**.
   - In the dialog that appears, click **Open** again to confirm.
   - Alternatively: go to **System Settings → Privacy & Security**, scroll down, and click **Open Anyway**.

> **Note:** The first launch may take a few seconds as macOS verifies the application.

---

## System Requirements

| Requirement | Minimum |
|-------------|---------|
| **Operating System** | macOS 13 (Ventura) or later |
| **Processor** | Apple Silicon (M1/M2/M3/M4) or Intel x86_64 |
| **Disk Space** | 512 MB available |
| **Graphics** | OpenGL 3.3+ capable GPU (all Macs since 2012) |

---

## Controls

| Action | Default Key |
|--------|-------------|
| Rotate Left | ← Arrow Left |
| Rotate Right | → Arrow Right |
| Thrust | ↑ Arrow Up |
| Brake | ↓ Arrow Down |
| Fire | Space |
| Special (Power-up) | Left Shift |
| Pause | Escape |
| Confirm / Continue | Enter |

> Controls are fully remappable in **Settings** from the main menu.

---

## How to Play

### Combat

Pilot your ship through waves of asteroids and enemy ships. Destroy them to collect **currency crystals** that drop from wreckage. Large asteroids split into smaller ones when destroyed — clear every fragment to advance to the next level.

### Shop

Between levels, your ship enters the **upgrade shop**. Fly into upgrade nodes to browse and purchase improvements with your collected currency. Choose wisely — each level gets harder.

### Upgrades

Improve your ship across five categories:

- **Weapons** — Faster fire rate, more projectiles, increased damage
- **Defense** — Stronger shields, faster regeneration
- **Mobility** — Better thrust, tighter turning
- **Economy** — Increased currency drops from destroyed objects
- **Repair** — Restore shield HP between levels

### Insurance

Protect your upgrades against death. Insurance costs currency each level but retains a fraction of your upgrades if you lose all shields. Choose between **Basic** (partial retention) and **Premium** (higher retention at higher cost) tiers — or go uninsured and risk it all.

### Scoring

Earn points for every asteroid and enemy destroyed. Larger asteroids and tougher enemies award more points. High scores are saved locally and viewable from the main menu.

---

## Game Modes

| Mode | Description |
|------|-------------|
| **Classic Endless** | The default experience — survive as long as possible through infinite levels of increasing difficulty. |
| **Practice / Training** | Learn the controls and experiment with reduced difficulty. Great for new players. |

---

## Building from Source

### Prerequisites

- Python 3.13 or later
- macOS (required for the Arcade graphics library)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/void-breaker.git
cd void-breaker

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Run from Source

```bash
source .venv/bin/activate
python -m asterax.app.src.main
```

### Build the macOS App Bundle

```bash
source .venv/bin/activate
./scripts/build_app.sh
# Output: dist/VoidBreaker.app
```

### Create the DMG Installer

```bash
source .venv/bin/activate
./scripts/create_dmg.sh
# Output: dist/VoidBreaker.dmg
```

### Run Tests

```bash
source .venv/bin/activate
pytest -q --cov=app/src --cov-report=term-missing
```

---

## Known Issues

| # | Issue | Workaround |
|---|-------|------------|
| 1 | Unsigned app triggers macOS Gatekeeper on first launch | Right-click → Open → Confirm, or System Settings → Privacy & Security → Open Anyway |
| 2 | DMG uses plain layout (no custom Finder icon positioning) | Functional as-is. Install `brew install create-dmg` before building for polished layout |
| 3 | Background music not yet implemented (music volume slider is non-functional) | Sound effects work fully; music support planned for a future release |

---

## Credits

Developed by Sean Meehan.

Built with [Python](https://www.python.org/) and the [Arcade](https://api.arcade.academy/) library.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.