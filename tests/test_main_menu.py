"""Tests for the Phase 5.2 main menu navigation system."""

from __future__ import annotations

import arcade
from asterax.app.src.config.difficulty_tables import DifficultyPreset
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.states.main_menu import MainMenuState


class FakeAudioManager:
    """Test double recording played sound names."""

    def __init__(self) -> None:
        """Initialize the recording list."""
        self.played: list[str] = []

    def play(self, name: str) -> None:
        """Record a played sound name."""
        self.played.append(name)


class FakeWindow:
    """Window test double for menu state unit tests."""

    def __init__(self) -> None:
        """Set up test-only window attributes used by MainMenuState."""
        self.width = 1280
        self.height = 960
        self.audio_manager = FakeAudioManager()
        self.input_manager = InputManager(GameSettings())
        self.persistence = _PersistenceStub(GameSettings())
        self.runtime_settings = self.persistence.load_settings()
        self.closed = False

    def close(self) -> None:
        """Record window close invocation."""
        self.closed = True


class RecordingStateMachine:
    """Minimal state machine test double for transition assertions."""

    def __init__(self) -> None:
        """Initialize transition recording storage."""
        self.switched_to: list[str] = []

    def switch_state(self, state: object) -> None:
        """Record the class name of the transitioned-to state instance."""
        self.switched_to.append(type(state).__name__)


class _PersistenceStub:
    """Persistence test double for menu difficulty selection tests."""

    def __init__(self, settings: GameSettings) -> None:
        """Store initial settings."""
        self._settings = settings

    def load_settings(self) -> GameSettings:
        """Return persisted settings."""
        return self._settings

    def save_settings(self, settings: GameSettings) -> None:
        """Persist updated settings."""
        self._settings = settings


def test_main_menu_initializes_with_six_options(monkeypatch) -> None:
    """Main menu should initialize required options including Practice."""
    monkeypatch.setattr(arcade, "get_window", lambda: FakeWindow())
    state = MainMenuState(RecordingStateMachine())

    assert len(state._menu_options) == 6
    assert [label for label, _ in state._menu_options] == [
        "New Game",
        "Practice",
        "How to Play",
        "Settings",
        "High Scores",
        "Quit",
    ]


def test_navigation_wraps_from_last_to_first_and_first_to_last(monkeypatch) -> None:
    """Up/down navigation should wrap around the option list boundaries."""
    monkeypatch.setattr(arcade, "get_window", lambda: FakeWindow())
    state = MainMenuState(RecordingStateMachine())
    state.on_enter()

    state._selected_index = len(state._menu_options) - 1
    state._navigate(1)
    assert state._selected_index == 0

    state._selected_index = 0
    state._navigate(-1)
    assert state._selected_index == len(state._menu_options) - 1


def test_select_transitions_to_correct_states(monkeypatch) -> None:
    """Each non-quit option should transition to the expected state."""
    window = FakeWindow()
    machine = RecordingStateMachine()
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = MainMenuState(machine)
    state.on_enter()

    expected_targets = {
        "new_game": "GameInitState",
        "practice": "PracticeConfigState",
        "how_to_play": "HowToPlayState",
        "settings": "SettingsScreenState",
        "high_scores": "HighScoresState",
    }

    for option_index, (_, target) in enumerate(state._menu_options):
        if target == "quit":
            continue
        state._selected_index = option_index
        state.on_key_press(arcade.key.ENTER, 0)
        if target == "new_game":
            state.on_key_press(arcade.key.ENTER, 0)
        state.on_update(1.0)
        assert machine.switched_to[-1] == expected_targets[target]


def test_new_game_persists_selected_difficulty(monkeypatch) -> None:
    """Selecting a difficulty before New Game should persist it in settings."""
    window = FakeWindow()
    machine = RecordingStateMachine()
    monkeypatch.setattr(arcade, "get_window", lambda: window)

    state = MainMenuState(machine)
    state.on_enter()
    state._selected_index = 0
    state.on_key_press(arcade.key.ENTER, 0)

    assert state._showing_difficulty_selection is True

    state.on_key_press(arcade.key.UP, 0)
    state.on_key_press(arcade.key.ENTER, 0)
    state.on_update(1.0)

    assert machine.switched_to[-1] == "GameInitState"
    assert (
        window.persistence.load_settings().difficulty == DifficultyPreset.CASUAL.value
    )


def test_quit_option_closes_window(monkeypatch) -> None:
    """Selecting quit should close the active Arcade window."""
    window = FakeWindow()
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = MainMenuState(RecordingStateMachine())
    state.on_enter()

    quit_index = next(
        index
        for index, (_, target) in enumerate(state._menu_options)
        if target == "quit"
    )
    state._selected_index = quit_index
    state.on_key_press(arcade.key.ENTER, 0)
    state.on_update(1.0)

    assert window.closed is True


def test_navigation_and_selection_play_expected_sounds(monkeypatch) -> None:
    """Navigation and selection actions should trigger menu audio cues."""
    window = FakeWindow()
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = MainMenuState(RecordingStateMachine())
    state.on_enter()

    state.on_key_press(arcade.key.DOWN, 0)
    state.on_key_press(arcade.key.ENTER, 0)

    assert "menu_nav" in window.audio_manager.played
    assert "menu_select" in window.audio_manager.played
