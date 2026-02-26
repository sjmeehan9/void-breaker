"""Tests for the Phase 5.3 how-to-play screen."""

from __future__ import annotations

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.states.how_to_play import HowToPlayState


class FakeWindow:
    """Window test double for how-to-play state tests."""

    def __init__(self) -> None:
        """Set up attributes read by HowToPlayState."""
        self.width = 1280
        self.height = 960
        self.input_manager = InputManager(GameSettings())


class RecordingStateMachine:
    """Minimal state machine test double for transition assertions."""

    def __init__(self) -> None:
        """Initialize transition recording storage."""
        self.switched_to: list[str] = []

    def switch_state(self, state: object) -> None:
        """Record class names of switched states."""
        self.switched_to.append(type(state).__name__)


def test_build_controls_text_reflects_default_bindings(monkeypatch) -> None:
    """Controls rows should be built from active default input bindings."""
    monkeypatch.setattr(arcade, "get_window", lambda: FakeWindow())
    state = HowToPlayState(RecordingStateMachine())

    assert state._build_controls_text() == [
        "Rotate Left::Left",
        "Rotate Right::Right",
        "Thrust::Up",
        "Fire::Space",
        "Brake::Down",
        "Pause/Back::Escape",
    ]


def test_escape_returns_to_main_menu(monkeypatch) -> None:
    """Escape should navigate back to the main menu state."""
    monkeypatch.setattr(arcade, "get_window", lambda: FakeWindow())
    machine = RecordingStateMachine()
    state = HowToPlayState(machine)

    state.on_key_press(arcade.key.ESCAPE, 0)

    assert machine.switched_to[-1] == "MainMenuState"
