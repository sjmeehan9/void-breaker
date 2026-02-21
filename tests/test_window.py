"""Tests for fixed timestep behaviour in the game window."""

import sys
from pathlib import Path
from types import ModuleType

import pytest

repo_root = Path(__file__).resolve().parents[1]
asterax_module = ModuleType("asterax")
asterax_module.__path__ = [str(repo_root)]  # type: ignore[attr-defined]
sys.modules.setdefault("asterax", asterax_module)

from asterax.app.src.window import MAX_FRAME_TIME, PHYSICS_DT, VoidBreakerWindow


def test_on_update_uses_fixed_timestep() -> None:
    """on_update should execute physics steps based on fixed dt increments."""
    window = object.__new__(VoidBreakerWindow)
    window.accumulator = 0.0

    steps: list[float] = []

    def record_step(dt: float) -> None:
        steps.append(dt)

    window._physics_step = record_step  # type: ignore[method-assign]
    window.on_update(PHYSICS_DT * 2.5)

    assert len(steps) == 2
    assert all(step == PHYSICS_DT for step in steps)
    assert window.accumulator == pytest.approx(PHYSICS_DT * 0.5)


def test_on_update_caps_large_delta_time() -> None:
    """on_update should cap frame time to avoid spiral-of-death behaviour."""
    window = object.__new__(VoidBreakerWindow)
    window.accumulator = 0.0

    steps: list[float] = []

    def record_step(dt: float) -> None:
        steps.append(dt)

    window._physics_step = record_step  # type: ignore[method-assign]
    window.on_update(MAX_FRAME_TIME * 2)

    assert len(steps) == int(MAX_FRAME_TIME / PHYSICS_DT)
