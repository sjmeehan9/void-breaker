"""Phase 5 settings persistence and remap integration tests."""

from __future__ import annotations

from pathlib import Path

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.persistence_manager import PersistenceManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.states.settings_screen import SettingsScreenState


class _AudioStub:
    def __init__(self) -> None:
        self.updated_with: GameSettings | None = None

    def update_settings(self, settings: GameSettings) -> None:
        self.updated_with = settings

    def play(self, _: str) -> None:
        return None


class _WindowStub:
    def __init__(self, settings: GameSettings) -> None:
        self.width = 1280
        self.height = 960
        self.persistence = PersistenceManager(base_dir=Path("."))
        self.persistence.save_settings(settings)
        self.input_manager = InputManager(settings)
        self.audio_manager = _AudioStub()


class _MachineStub:
    def __init__(self) -> None:
        self.pop_calls = 0

    def pop_state(self) -> None:
        self.pop_calls += 1

    def switch_state(self, state: object) -> None:
        del state


def _select_row(state: SettingsScreenState, row_name: str) -> None:
    for index, item in enumerate(state._settings_items):
        if item.name == row_name:
            state._selected_index = index
            return
    raise AssertionError(f"Missing row: {row_name}")


def test_settings_adjust_rebind_and_round_trip(monkeypatch, tmp_path: Path) -> None:
    """Settings support slider clamping, duplicate rebind handling, and persistence."""
    settings = GameSettings(master_volume=0.9, key_fire="SPACE", key_thrust="UP")
    window = _WindowStub(settings)
    window.persistence = PersistenceManager(base_dir=tmp_path)
    window.persistence.save_settings(settings)
    monkeypatch.setattr(arcade, "get_window", lambda: window)

    state = SettingsScreenState(_MachineStub(), return_to="pause")
    state.on_enter()

    _select_row(state, "Master Volume")
    state._adjust_setting(1)
    assert state._settings.master_volume == 1.0

    _select_row(state, "Fire")
    state._start_rebind()
    state._complete_rebind(arcade.key.UP)
    assert state._settings.key_fire == "UP"
    assert state._settings.key_thrust == "UNBOUND"

    reloaded = window.persistence.load_settings()
    assert reloaded.key_fire == "UP"
    assert reloaded.key_thrust == "UNBOUND"
