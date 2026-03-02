# VoidBreaker — Final QA Checklist

**Version:** 1.0.0
**Date:** 2026-03-02
**Component:** 6.5 — Final QA & Cross-Platform Smoke Test
**Test Target:** Packaged `VoidBreaker.app` (from `dist/VoidBreaker.dmg`)

---

## Severity Ratings

| Rating | Meaning |
|--------|---------|
| **P0** | Blocker — prevents release; app unlaunchable or data-loss risk |
| **P1** | Critical — core gameplay broken; must fix before release |
| **P2** | Major — significant feature degradation; should fix if possible |
| **P3** | Minor — cosmetic or low-impact issue; acceptable for v1.0 |
| **P4** | Cosmetic — polish issue; nice-to-fix for future release |

---

## 1. Installation & Launch

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 1.1 | DMG file mounts in Finder without errors | | P0 | Double-click `VoidBreaker.dmg` |
| 1.2 | Mounted DMG shows `VoidBreaker.app` and `Applications` alias | | P0 | Visual check in Finder |
| 1.3 | Drag-to-install copies app to `/Applications/` | | P0 | Drag app icon to Applications alias |
| 1.4 | App launches from `/Applications/VoidBreaker.app` | | P0 | Double-click in Finder |
| 1.5 | No terminal window appears on launch | | P1 | Verify no Terminal.app window opens |
| 1.6 | Window title reads "VoidBreaker" | | P2 | Check title bar text |
| 1.7 | Gatekeeper workaround works (right-click → Open → confirm) | | P1 | For unsigned app on macOS 13+ |
| 1.8 | App icon displays correctly in Dock and Finder | | P3 | Should show custom VoidBreaker icon |
| 1.9 | App launches on macOS 13 (Ventura) or later | | P1 | Verify minimum OS version support |

---

## 2. Main Menu

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 2.1 | Main menu displays on launch with title "VoidBreaker" | | P0 | |
| 2.2 | All menu items visible: New Game, How to Play, Settings, High Scores, Practice, Quit | | P1 | |
| 2.3 | Keyboard navigation (Up/Down arrows) moves between menu items | | P1 | |
| 2.4 | Enter/Return selects the highlighted menu item | | P1 | |
| 2.5 | Menu navigation sound (`menu_nav`) plays on cursor movement | | P2 | |
| 2.6 | Menu selection sound (`menu_select`) plays on confirm | | P2 | |
| 2.7 | Difficulty selector shows Casual / Classic / Hard presets | | P2 | |
| 2.8 | Difficulty descriptions display correctly for each preset | | P3 | Casual: "Fewer asteroids…", Classic: "Balanced…", Hard: "More pressure…" |
| 2.9 | Quit option exits the application | | P1 | |
| 2.10 | Starfield background renders behind menu | | P3 | |

---

## 3. Settings

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 3.1 | Settings screen accessible from main menu | | P1 | |
| 3.2 | Key remapping works for all controls (Rotate L/R, Thrust, Brake, Fire, Special, Pause) | | P1 | Change a binding, return to game, verify |
| 3.3 | Master volume slider adjusts overall game volume | | P2 | |
| 3.4 | SFX volume slider adjusts sound effect volume | | P2 | |
| 3.5 | Music volume slider present (no-op is acceptable for v1.0) | | P3 | Music not implemented |
| 3.6 | Colorblind mode toggle works | | P2 | Enable → visual indicators should change |
| 3.7 | Screen shake setting changes (off / low / medium / high) | | P2 | |
| 3.8 | Fire mode toggle works (hold / toggle) | | P2 | |
| 3.9 | Difficulty preset can be changed from settings | | P2 | |
| 3.10 | Settings persist across app restart | | P1 | Change a setting, quit, relaunch, verify |
| 3.11 | Settings saved to `~/Library/Application Support/VoidBreaker/settings.json` | | P1 | Check file exists and contents |
| 3.12 | Return to main menu from settings works | | P1 | |

---

## 4. Combat

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 4.1 | New Game starts combat phase with player ship centered | | P0 | |
| 4.2 | Ship rotates left/right with arrow keys (or remapped keys) | | P0 | |
| 4.3 | Ship thrusts forward with Up arrow | | P0 | |
| 4.4 | Ship brakes with Down arrow (increased drag) | | P1 | |
| 4.5 | Inertial physics feel correct (momentum, drift, drag) | | P1 | Ship should coast when not thrusting |
| 4.6 | Ship fires projectile with Space (or remapped fire key) | | P0 | |
| 4.7 | Fire cooldown prevents continuous rapid fire | | P2 | |
| 4.8 | Thrust trail visual appears when thrusting | | P3 | Ship sprite or particle trail |
| 4.9 | Asteroids spawn at level start (away from player) | | P0 | |
| 4.10 | Large asteroids split into medium asteroids on destruction | | P1 | |
| 4.11 | Medium asteroids split into small asteroids on destruction | | P1 | |
| 4.12 | Small asteroids are destroyed without splitting | | P1 | |
| 4.13 | Asteroids wrap at screen edges | | P1 | |
| 4.14 | Ship wraps at screen edges | | P1 | |
| 4.15 | Projectiles wrap at screen edges (or expire at range limit) | | P2 | |
| 4.16 | Currency crystals drop from destroyed asteroids | | P1 | |
| 4.17 | Currency pickups collectible by flying into them | | P1 | |
| 4.18 | Pickup currency sound (`pickup_currency`) plays on collection | | P2 | |
| 4.19 | Enemy ships appear at configured levels | | P1 | Check difficulty tables for spawn level |
| 4.20 | Enemy ships fire projectiles at the player | | P1 | |
| 4.21 | Enemy projectiles damage player (shield reduction) | | P1 | |
| 4.22 | Player projectiles destroy enemy ships | | P1 | |
| 4.23 | Enemy explosion sound plays on destruction | | P2 | |
| 4.24 | Player hit sound plays when shield damaged | | P2 | |
| 4.25 | Damage flash visual effect on player hit | | P2 | |
| 4.26 | Invulnerability period after taking damage (~0.75s) | | P1 | Ship should flash/blink |
| 4.27 | HUD displays: shields, score, level, currency | | P1 | |
| 4.28 | HUD values update correctly during gameplay | | P1 | |
| 4.29 | Asteroid explosion particles render (3 sizes) | | P2 | |
| 4.30 | Fire sound (`fire`) plays on each shot | | P2 | |
| 4.31 | Explosion sounds play with correct size variant | | P2 | `explode_small`, `explode_medium`, `explode_large` |
| 4.32 | Level clear triggers after all asteroids and enemies destroyed | | P0 | |
| 4.33 | Level clear sound (`level_clear`) plays | | P2 | |
| 4.34 | Level number increments after clearing a level | | P1 | |
| 4.35 | Difficulty increases with level (more asteroids, faster enemies) | | P1 | Compare level 1 vs level 5+ |
| 4.36 | Buff pickups appear and function (damage, heal, shield, speed) | | P2 | |
| 4.37 | Buff pickup sound (`pickup_buff`) plays on collection | | P2 | |
| 4.38 | Shield low warning sound (`shield_low`) plays at low health | | P3 | |

---

## 5. Shop

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 5.1 | Shop phase activates after clearing a combat level | | P0 | |
| 5.2 | Upgrade nodes arranged in circle layout | | P1 | Weapon, Defense, Mobility, Economy, Repair, Insurance, Continue |
| 5.3 | Ship controls work in shop (fly between nodes) | | P1 | |
| 5.4 | Flying into a node triggers purchase interaction | | P1 | |
| 5.5 | Currency deducted on successful purchase | | P1 | |
| 5.6 | Shop purchase sound (`shop_purchase`) plays on buy | | P2 | |
| 5.7 | Denied sound (`shop_denied`) plays on insufficient funds | | P2 | |
| 5.8 | Ship re-centres after each purchase | | P2 | |
| 5.9 | "Continue" node returns to combat (next level) | | P0 | |
| 5.10 | Upgrade effects visible in next combat level | | P1 | E.g., faster fire rate, more shields |
| 5.11 | Node labels and prices display correctly | | P2 | |
| 5.12 | Currency display accurate in shop HUD | | P1 | |

---

## 6. Insurance

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 6.1 | Insurance purchasable in shop (Off / Basic / Premium) | | P1 | |
| 6.2 | Insurance cost deducted each level (if active) | | P1 | |
| 6.3 | Insurance deduction sound (`insurance_deduct`) plays | | P3 | |
| 6.4 | Premium insurance retains all upgrades on death | | P1 | |
| 6.5 | Basic insurance retains ~50% of upgrades on death | | P1 | |
| 6.6 | No insurance (Off) retains no upgrades on death | | P1 | |
| 6.7 | Insurance status visible in HUD or shop | | P2 | |

---

## 7. Game Over & High Scores

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 7.1 | Game over triggers when shields reach zero | | P0 | |
| 7.2 | Game over sound (`game_over`) plays | | P2 | |
| 7.3 | Run summary screen displays (score, level reached, enemies destroyed) | | P1 | |
| 7.4 | High score entry allows initials input (3 characters) | | P1 | |
| 7.5 | High score saved to persistent storage | | P1 | Check `~/Library/Application Support/VoidBreaker/` |
| 7.6 | High score appears on leaderboard screen | | P1 | |
| 7.7 | Leaderboard persists across app restarts | | P1 | Quit, relaunch, check High Scores |
| 7.8 | Return to main menu from game over works | | P1 | |
| 7.9 | Starting a new game after game over works cleanly | | P1 | No state leakage from previous run |

---

## 8. Audio

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 8.1 | `fire.wav` — plays on player shooting | | P2 | |
| 8.2 | `hit.wav` / `player_hit.wav` — plays on player taking damage | | P2 | |
| 8.3 | `explode_small.wav` — plays on small asteroid destruction | | P2 | |
| 8.4 | `explode_medium.wav` — plays on medium asteroid destruction | | P2 | |
| 8.5 | `explode_large.wav` — plays on large asteroid destruction | | P2 | |
| 8.6 | `enemy_explode.wav` — plays on enemy ship destruction | | P2 | |
| 8.7 | `enemy_fire.wav` — plays when enemy fires | | P3 | |
| 8.8 | `pickup_currency.wav` — plays on currency crystal collection | | P2 | |
| 8.9 | `pickup_buff.wav` — plays on buff pickup collection | | P2 | |
| 8.10 | `shop_purchase.wav` — plays on successful shop purchase | | P2 | |
| 8.11 | `shop_denied.wav` — plays on denied shop interaction | | P2 | |
| 8.12 | `level_clear.wav` — plays on level completion | | P2 | |
| 8.13 | `game_over.wav` — plays on game over | | P2 | |
| 8.14 | `menu_nav.wav` — plays on menu cursor movement | | P2 | |
| 8.15 | `menu_select.wav` — plays on menu selection confirm | | P2 | |
| 8.16 | `shield_low.wav` — plays at low shield warning | | P3 | |
| 8.17 | `insurance_deduct.wav` — plays on insurance cost deduction | | P3 | |
| 8.18 | Master volume affects all sounds proportionally | | P2 | |
| 8.19 | SFX volume affects sound effects independently | | P2 | |
| 8.20 | No audio glitches, pops, or crashes during extended play | | P1 | |

---

## 9. Visual Effects

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 9.1 | Explosion particles render on asteroid destruction (3 size variants) | | P2 | |
| 9.2 | Thrust trail visible when ship is accelerating | | P3 | |
| 9.3 | Pickup sparkle/particle effect on currency collection | | P3 | |
| 9.4 | Damage flash on player ship when hit | | P2 | |
| 9.5 | Screen shake on damage (when enabled in settings) | | P2 | |
| 9.6 | Screen shake respects settings (off disables, intensity scales) | | P2 | |
| 9.7 | Level transition effect between combat and shop | | P3 | |
| 9.8 | Starfield background renders in all states | | P3 | |
| 9.9 | All sprites load without missing-texture errors | | P0 | No pink/magenta placeholder boxes |
| 9.10 | All sprites correct size and appearance | | P2 | Visual inspection |
| 9.11 | Colorblind mode changes visual indicators when enabled | | P2 | |

---

## 10. Practice / Training Mode

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 10.1 | Practice mode accessible from main menu | | P1 | |
| 10.2 | Practice mode launches into combat | | P1 | |
| 10.3 | Asteroids-only toggle works (no enemies when enabled) | | P2 | |
| 10.4 | Infinite shields toggle works (ship takes no damage) | | P2 | |
| 10.5 | No high score recording in practice mode | | P2 | Score should not save to leaderboard |
| 10.6 | Return to main menu works from practice mode | | P1 | |

---

## 11. Pause System

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 11.1 | Pressing Escape during combat pauses the game | | P1 | |
| 11.2 | All on-screen action freezes while paused | | P1 | |
| 11.3 | Pause overlay/menu displays (Resume, Restart, Exit to Menu) | | P1 | |
| 11.4 | Resume resumes gameplay from exact state | | P1 | |
| 11.5 | Restart begins a new game from level 1 | | P1 | |
| 11.6 | Exit to Menu returns to main menu cleanly | | P1 | |
| 11.7 | Pause works during shop phase | | P2 | |

---

## 12. Performance

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 12.1 | No noticeable frame drops during normal play (levels 1–5) | | P1 | |
| 12.2 | No frame drops during intense combat (20+ entities on screen) | | P1 | |
| 12.3 | No input lag perceptible during gameplay | | P1 | |
| 12.4 | No visual stuttering or tearing | | P2 | |
| 12.5 | App memory usage stable (no continuous growth) over 15+ minutes | | P1 | Check Activity Monitor |
| 12.6 | App CPU usage reasonable during gameplay | | P2 | Should not peg a core at 100% |

---

## 13. Cross-Platform (Optional)

| # | Test Case | Pass/Fail | Severity | Notes |
|---|-----------|-----------|----------|-------|
| 13.1 | Windows: app launches (if cross-build available) | | P3 | Optional for v1.0 |
| 13.2 | Windows: basic gameplay works (combat, controls) | | P3 | Optional |
| 13.3 | Windows: persistence works (settings, high scores) | | P3 | Optional |
| 13.4 | Linux: app launches (if cross-build available) | | P3 | Optional |
| 13.5 | Linux: basic gameplay works | | P3 | Optional |
| 13.6 | Linux: persistence works | | P3 | Optional |

---

## Full Game Loop Smoke Test

> Complete this end-to-end playthrough on the **packaged `.app`** to verify the full player experience:

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1 | Launch `VoidBreaker.app` from `/Applications/` | Main menu displays | | |
| 2 | Navigate to Settings, change a volume slider | Setting updates visually | | |
| 3 | Return to main menu | Menu displays correctly | | |
| 4 | Select "New Game" with Classic difficulty | Combat starts, ship centered, asteroids spawn | | |
| 5 | Play through Level 1 (destroy all asteroids) | Level clears, shop activates | | |
| 6 | Purchase an upgrade in the shop | Currency deducted, purchase sound plays | | |
| 7 | Select Continue node, play Level 2 | Combat resumes with difficulty increase | | |
| 8 | Continue playing through Level 3–5 | Enemies appear, difficulty scales | | |
| 9 | Use shop each level, purchase insurance | Insurance node accessible, cost shown | | |
| 10 | Pause during combat (Escape), then resume | Game freezes/resumes correctly | | |
| 11 | Die (let shields reach zero) | Game over screen displays with run summary | | |
| 12 | Enter initials for high score | Initials entry works, score saved | | |
| 13 | Verify score on High Scores screen | Score appears on leaderboard | | |
| 14 | Quit app, relaunch from Applications | App restarts cleanly | | |
| 15 | Check High Scores — previous score persists | Leaderboard shows saved score | | |
| 16 | Check Settings — previous changes persist | Settings reflect earlier changes | | |
| 17 | Start Practice mode, verify reduced difficulty | Practice options work | | |
| 18 | Return to menu, select How to Play | Instructions screen displays | | |
| 19 | Return to menu, Quit | App exits cleanly | | |

---

## Known Issues

| # | Issue | Severity | Workaround | Status |
|---|-------|----------|------------|--------|
| K1 | Unsigned app triggers macOS Gatekeeper on first launch | P3 | Right-click → Open → Confirm, or System Settings → Privacy & Security → Open Anyway | Expected (v1.0 unsigned) |
| K2 | `create-dmg` not installed — DMG uses plain `hdiutil` layout | P4 | Functional but no custom Finder icon layout. Install `brew install create-dmg` for polish | Documented in 6.3 |
| K3 | Background music not implemented (`play_music` is no-op) | P3 | Music volume slider present but non-functional | By design for v1.0 |

*Additional issues discovered during QA testing should be appended here with severity and workaround.*

---

## Automated Verification Results

> Completed by AI Agent as part of Component 6.5 delivery.

| Check | Command | Result | Notes |
|-------|---------|--------|-------|
| Code quality | `python scripts/evals.py` | **PASS** | No TODO/FIXME markers, all docstrings present |
| Test suite | `pytest -q --cov=app/src --cov-report=term-missing` | **PASS** | 341 passed, 77% coverage |
| Formatting | `black --check app/src/` | **PASS** | 58 files unchanged (3 reformatted during QA) |
| Import sorting | `isort --check-only app/src/` | **PASS** | No import ordering issues |
| Build | `./scripts/build_app.sh` | **PASS** | `dist/VoidBreaker.app` exists (5.5 MB executable) |
| DMG | `./scripts/create_dmg.sh` | **PASS** | `dist/VoidBreaker.dmg` exists (50 MB) |

---

## QA Sign-Off

| Role | Name | Date | Verdict |
|------|------|------|---------|
| QA Tester (Human) | | | |
| AI Agent | GitHub Copilot | 2026-03-02 | Checklist created, automated checks executed |

---

*This checklist should be completed on a clean macOS installation or separate user account whenever possible, to catch environment-specific dependencies that may not exist on end-user machines.*
