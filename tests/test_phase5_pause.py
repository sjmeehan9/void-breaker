"""Phase 5 pause overlay freeze/resume coverage."""

from __future__ import annotations

from types import SimpleNamespace

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.states.pause import PauseState
from asterax.app.src.states.state_machine import StateMachine


class _BaseState:
    def __init__(self) -> None:
        self.update_calls = 0

    def on_enter(self) -> None:
        return None

    def on_exit(self) -> None:
        return None

    def on_update(self, _: float) -> None:
        self.update_calls += 1

    def on_draw(self) -> None:
        return None

    def on_key_press(self, key: int, modifiers: int) -> None:
        del key, modifiers

    def on_key_release(self, key: int, modifiers: int) -> None:
        del key, modifiers


def test_pause_freezes_underlying_state_and_resume_unfreezes(monkeypatch) -> None:
    """Pause overlay blocks underlying updates and resume restores them."""
    window = SimpleNamespace(
        width=1280,
        height=960,
        input_manager=InputManager(GameSettings()),
        audio_manager=SimpleNamespace(play=lambda _: None),
        persistence=SimpleNamespace(),
    )
    monkeypatch.setattr(arcade, "get_window", lambda: window)

    machine = StateMachine()
    base = _BaseState()
    machine.switch_state(base)
    machine.push_state(PauseState(machine))

    machine.update(0.016)
    assert base.update_calls == 0

    pause_state = machine.current_state
    assert isinstance(pause_state, PauseState)
    pause_state.on_key_press(window.input_manager.get_binding("pause"), 0)
    machine.update(0.016)

    assert base.update_calls == 1
