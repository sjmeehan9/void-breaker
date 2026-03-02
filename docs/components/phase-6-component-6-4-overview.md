# Component 6.4 Overview — Performance Validation

## Scope Delivered

Component 6.4 was implemented to validate runtime performance and memory stability for both source and packaged execution paths. The implementation includes an automated profiling workflow, deterministic stress-scene orchestration at required peak entity counts, and documented pass/fail outcomes.

## What Was Built

- Added `scripts/profile_performance.py` to automate:
  - Source-mode profiling (`python -m asterax.app.src.main`)
  - Packaged-mode profiling (`dist/VoidBreaker.app/Contents/MacOS/VoidBreaker`)
  - Frame-time metric capture from in-app stress mode
  - Process memory sampling to CSV via `psutil`
  - Leak detection using linear RSS slope (MB/min)
- Added environment-gated stress launch path in `app/src/main.py`.
- Extended `CombatPhaseState` with a deterministic stress mode that spawns:
  - 100 asteroids
  - 10 enemies
  - 15 player projectiles
  - 20 enemy projectiles
  - 40 pickups
  - 300 active particles
- Added in-app frame-metrics JSON export and automatic benchmark shutdown.
- Produced `docs/performance-report.md` with measured results and conclusions.

## Key Files

- `scripts/profile_performance.py`
- `app/src/main.py`
- `app/src/states/combat.py`
- `docs/performance-report.md`
- `docs/performance-data/*`

## Validation Executed

- Source mode: automated profiling run with frame and memory metrics.
- Packaged mode: automated profiling run including required 30-minute memory session.
- Results confirmed:
  - Average frame time under 16.67 ms
  - Max frame time under 33 ms
  - No memory leak trend in the 30-minute packaged run

## Outcome

Component 6.4 acceptance criteria are satisfied and documented.
