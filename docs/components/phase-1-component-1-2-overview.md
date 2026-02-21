# Phase 1 Component 1.2: Project Structure & Entry Point

## Overview
Component 1.2 establishes the executable game shell and repository layout required by the Phase 1 architecture. It adds the runtime entry point, core window loop timing, package initializers, asset placeholders, and early quality-eval scaffolding.

## Delivered Implementation
- Added the full Phase 1 directory scaffold under `app/src`, `app/config`, `app/docs`, `assets`, `scripts`, and `tests`.
- Created required `__init__.py` files for all Python packages.
- Implemented `app/src/main.py` with a minimal `main() -> None` that constructs `VoidBreakerWindow` and starts `arcade.run()`.
- Implemented `app/src/window.py` with:
  - constants `PHYSICS_DT = 1.0 / 60.0` and `MAX_FRAME_TIME = 0.25`
  - fixed-rate target via `self.set_update_rate(PHYSICS_DT)`
  - accumulator-based fixed timestep loop in `on_update`
  - black-frame rendering in `on_draw`
  - key input handlers and physics-step method placeholders for later state-machine integration.
- Added placeholder `.gitkeep` files for `assets/sprites`, `assets/sounds`, and `assets/fonts`.
- Added `scripts/evals.py` to enforce no TODO/FIXME markers and public class/function docstrings under `app/src`.

## Validation
- Focused tests:
  - `tests/test_main.py` verifies entry-point bootstrap order (window creation then `arcade.run`).
  - `tests/test_window.py` verifies fixed-step accumulation and frame-time clamping behavior.
- Quality checks: `black --check app/src scripts tests`, `isort --check-only app/src scripts tests`, and `python3 scripts/evals.py` all pass.
- Visual/manual check: a window render was executed in a virtual display and captured as a black frame screenshot, confirming initial draw behavior.

## Notes for Next Components
This component intentionally keeps subsystem wiring out of `main.py` and `window.py` beyond timing/render shell responsibilities, so Component 1.3 can cleanly integrate the state machine into update/draw/input delegation.
