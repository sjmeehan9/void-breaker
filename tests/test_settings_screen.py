"""Tests for the Phase 5.4 settings screen."""

from __future__ import annotations

from pathlib import Path

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.persistence_manager import PersistenceManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.states.settings_screen import SettingsScreenState


class FakePersistence:
    """Persistence test double for settings state tests."""

    def __init__(self, initial_settings: GameSettings) -> None:
        """Initialize test persistence with a settings payload.

        Args:
            initial_settings: Settings to return from load calls.
        """
        self._settings = initial_settings
        self.saved_settings: GameSettings | None = None

    def load_settings(self) -> GameSettings:
        """Return the current settings payload."""
        return self._settings

    def save_settings(self, settings: GameSettings) -> None:
        """Capture saved settings and update load payload.

        Args:
            settings: Settings instance passed from state.
        """
        self.saved_settings = settings
        self._settings = settings


class FakeAudioManager:
    """Audio manager test double for settings interactions."""

    def __init__(self) -> None:
        """Track audio update and playback calls."""
        self.updated_with: GameSettings | None = None
        self.played: list[str] = []

    def update_settings(self, settings: GameSettings) -> None:
        """Record latest settings update.

        Args:
            settings: Updated settings instance.
        """
        self.updated_with = settings

    def play(self, name: str) -> None:
        """Record played sound names.

        Args:
            name: Logical sound identifier.
        """
        self.played.append(name)


class FakeWindow:
    """Window test double exposing settings dependencies."""

    def __init__(self, settings: GameSettings) -> None:
        """Initialize fake window managers and dimensions.

        Args:
            settings: Initial settings for managers.
        """
        self.width = 1280
        self.height = 960
        self.persistence = FakePersistence(settings)
        self.input_manager = InputManager(settings)
        self.audio_manager = FakeAudioManager()


class RecordingStateMachine:
    """Minimal state machine test double for transition assertions."""

    def __init__(self) -> None:
        """Initialize transition recording storage."""
        self.switched_to: list[str] = []

    def switch_state(self, state: object) -> None:
        """Record class names of switched states.

        Args:
            state: State instance passed to switch.
        """
        self.switched_to.append(type(state).__name__)


def _set_selected_by_name(state: SettingsScreenState, label: str) -> None:
    """Select a row by its display name.

    Args:
        state: Settings state under test.
        label: Row label to target.
    """
    for index, item in enumerate(state._settings_items):
        if item.name == label:
            state._selected_index = index
            return
    raise AssertionError(f"Missing settings row: {label}")


def test_adjust_setting_clamps_slider_in_tenths(monkeypatch) -> None:
    """Slider adjustments should clamp in 0.1 increments from 0.0 to 1.0."""
    window = FakeWindow(GameSettings(master_volume=0.9))
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = SettingsScreenState(RecordingStateMachine())
    state.on_enter()

    _set_selected_by_name(state, "Master Volume")
    state._adjust_setting(1)
    assert state._settings.master_volume == 1.0

    state._adjust_setting(1)
    assert state._settings.master_volume == 1.0

    for _ in range(12):
        state._adjust_setting(-1)
    assert state._settings.master_volume == 0.0


def test_toggle_setting_flips_boolean(monkeypatch) -> None:
    """Toggle rows should flip their boolean value and persist."""
    window = FakeWindow(GameSettings(autofire=False))
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = SettingsScreenState(RecordingStateMachine())
    state.on_enter()

    _set_selected_by_name(state, "Autofire")
    state._toggle_setting()

    assert state._settings.autofire is True
    assert window.persistence.saved_settings is not None


def test_rebind_clears_duplicate_binding(monkeypatch) -> None:
    """Rebinding to an occupied key should clear the previous action binding."""
    settings = GameSettings(key_fire="SPACE", key_thrust="UP")
    window = FakeWindow(settings)
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = SettingsScreenState(RecordingStateMachine())
    state.on_enter()

    _set_selected_by_name(state, "Fire")
    state._start_rebind()
    state._complete_rebind(arcade.key.UP)

    assert state._settings.key_fire == "UP"
    assert state._settings.key_thrust == "UNBOUND"
    assert window.input_manager.get_binding("fire") == arcade.key.UP
    assert window.input_manager.get_binding("thrust") == -1


def test_reset_to_defaults_restores_default_values(monkeypatch) -> None:
    """Reset action should restore factory-default settings."""
    custom = GameSettings(
        master_volume=0.2,
        music_volume=0.1,
        sfx_volume=0.3,
        key_fire="RSHIFT",
        autofire=True,
        fire_mode="tap",
        colorblind_mode=True,
        screen_shake="off",
        difficulty="hard",
    )
    window = FakeWindow(custom)
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = SettingsScreenState(RecordingStateMachine())
    state.on_enter()

    state._reset_to_defaults()

    assert state._settings == GameSettings()
    assert window.input_manager.get_binding("fire") == arcade.key.SPACE


def test_settings_round_trip_through_persistence(tmp_path: Path) -> None:
    """Saved settings should load back with identical values."""
    persistence = PersistenceManager(base_dir=tmp_path)
    source = GameSettings(
        master_volume=0.7,
        music_volume=0.2,
        sfx_volume=0.9,
        key_rotate_left="A",
        key_rotate_right="D",
        key_thrust="W",
        key_fire="SPACE",
        key_brake="S",
        key_special="RSHIFT",
        key_pause="TAB",
        fire_mode="tap",
        autofire=True,
        colorblind_mode=True,
        screen_shake="low",
        difficulty="casual",
        fullscreen=True,
        resolution=(1920, 1080),
    )

    persistence.save_settings(source)
    loaded = persistence.load_settings()

    assert loaded.to_dict() == source.to_dict()
