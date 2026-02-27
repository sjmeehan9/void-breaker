"""Tests for Phase 5.6 pause overlay behavior."""

from __future__ import annotations

from types import SimpleNamespace

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.states.main_menu import MainMenuState
from asterax.app.src.states.pause import PauseState
from asterax.app.src.states.settings_screen import SettingsScreenState
from asterax.app.src.states.state_machine import StateMachine


class RecordingState:
    """Simple state that tracks lifecycle and update calls."""

    def __init__(self) -> None:
        self.enter_calls = 0
        self.exit_calls = 0
        self.update_calls = 0

    def on_enter(self) -> None:
        self.enter_calls += 1

    def on_exit(self) -> None:
        self.exit_calls += 1

    def on_update(self, delta_time: float) -> None:
        del delta_time
        self.update_calls += 1

    def on_draw(self) -> None:
        return None

    def on_key_press(self, key: int, modifiers: int) -> None:
        del key, modifiers

    def on_key_release(self, key: int, modifiers: int) -> None:
        del key, modifiers


class _WindowStub:
    """Window test double exposing required manager attributes."""

    def __init__(self) -> None:
        settings = GameSettings()
        self.width = 1280
        self.height = 960
        self.input_manager = InputManager(settings)
        self.audio_manager = SimpleNamespace(play=lambda name: None)
        self.persistence = SimpleNamespace()
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _MachineStub:
    """Minimal machine stub for direct PauseState action testing."""

    def __init__(self) -> None:
        self.pushed: object | None = None
        self.popped = False
        self.switched: object | None = None

    def push_state(self, state: object) -> None:
        self.pushed = state

    def pop_state(self) -> None:
        self.popped = True

    def switch_state(self, state: object) -> None:
        self.switched = state


def test_pause_push_does_not_exit_underlying_state(monkeypatch) -> None:
    """Overlay push should not call underlying on_exit lifecycle."""
    machine = StateMachine()
    base_state = RecordingState()
    window = _WindowStub()
    monkeypatch.setattr(arcade, "get_window", lambda: window)

    machine.switch_state(base_state)
    assert base_state.enter_calls == 1

    machine.push_state(PauseState(machine))

    assert base_state.exit_calls == 0


def test_pause_resume_pops_overlay_and_restores_updates(monkeypatch) -> None:
    """Pause key in pause menu should resume by popping only the overlay."""
    machine = StateMachine()
    base_state = RecordingState()
    window = _WindowStub()
    monkeypatch.setattr(arcade, "get_window", lambda: window)

    machine.switch_state(base_state)
    machine.push_state(PauseState(machine))
    machine.update(0.016)
    assert base_state.update_calls == 0

    pause_state = machine.current_state
    assert isinstance(pause_state, PauseState)
    pause_state.on_key_press(window.input_manager.get_binding("pause"), 0)

    assert machine.current_state is base_state
    machine.update(0.016)
    assert base_state.update_calls == 1


def test_pause_restart_switches_to_fresh_run(monkeypatch) -> None:
    """Selecting Restart Run should switch to game initialization state."""
    window = _WindowStub()
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    machine = _MachineStub()
    pause = PauseState(machine)

    pause._selected_index = 1
    pause.on_key_press(arcade.key.ENTER, 0)

    assert machine.switched is not None
    assert type(machine.switched).__name__ == "GameInitState"


def test_pause_exit_to_menu_switches_main_menu(monkeypatch) -> None:
    """Selecting Exit to Menu should switch to MainMenuState."""
    window = _WindowStub()
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    machine = _MachineStub()
    pause = PauseState(machine)

    pause._selected_index = 3
    pause.on_key_press(arcade.key.ENTER, 0)

    assert isinstance(machine.switched, MainMenuState)


def test_pause_settings_pushes_settings_overlay(monkeypatch) -> None:
    """Selecting Settings should push settings over pause with pause return target."""
    window = _WindowStub()
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    machine = _MachineStub()
    pause = PauseState(machine)

    pause._selected_index = 2
    pause.on_key_press(arcade.key.ENTER, 0)

    assert isinstance(machine.pushed, SettingsScreenState)
    assert machine.pushed._return_to == "pause"  # noqa: SLF001
