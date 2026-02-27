"""Phase 5 menu/screen integration coverage tests."""

from __future__ import annotations

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings, HighScoreEntry
from asterax.app.src.states.high_scores import HighScoresState
from asterax.app.src.states.how_to_play import HowToPlayState
from asterax.app.src.states.main_menu import MainMenuState


class _AudioStub:
    def __init__(self) -> None:
        self.played: list[str] = []

    def play(self, sound_name: str) -> None:
        self.played.append(sound_name)


class _PersistenceStub:
    def __init__(self) -> None:
        self._settings = GameSettings()
        self._scores: list[HighScoreEntry] = []

    def load_settings(self) -> GameSettings:
        return self._settings

    def save_settings(self, settings: GameSettings) -> None:
        self._settings = settings

    def load_high_scores(self) -> list[HighScoreEntry]:
        return list(self._scores)


class _WindowStub:
    def __init__(self) -> None:
        self.width = 1280
        self.height = 960
        self.persistence = _PersistenceStub()
        self.runtime_settings = self.persistence.load_settings()
        self.audio_manager = _AudioStub()
        self.input_manager = InputManager(self.runtime_settings)
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _MachineStub:
    def __init__(self) -> None:
        self.switched: list[str] = []

    def switch_state(self, state: object) -> None:
        self.switched.append(type(state).__name__)


def test_main_menu_navigation_and_selection(monkeypatch) -> None:
    """Menu keeps required options and supports wrapped keyboard navigation."""
    window = _WindowStub()
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = MainMenuState(_MachineStub())
    state.on_enter()

    labels = [label for label, _ in state._menu_options]
    assert labels[:5] == [
        "New Game",
        "Practice",
        "How to Play",
        "Settings",
        "High Scores",
    ]

    state._selected_index = len(state._menu_options) - 1
    state.on_key_press(arcade.key.DOWN, 0)
    assert state._selected_index == 0

    state.on_key_press(arcade.key.ENTER, 0)
    state.on_key_press(arcade.key.ENTER, 0)
    state.on_update(1.0)
    assert "menu_nav" in window.audio_manager.played
    assert "menu_select" in window.audio_manager.played


def test_how_to_play_and_high_scores_logic(monkeypatch) -> None:
    """How-to-play binding text and high-score filtering behave as expected."""
    window = _WindowStub()
    window.persistence._scores = [
        HighScoreEntry(
            name="AAA",
            score=500,
            level_reached=8,
            difficulty="hard",
            enemies_destroyed=15,
            currency_collected=60,
            currency_spent=30,
            date="2026-02-27T12:00:00+00:00",
        ),
        HighScoreEntry(
            name="BBB",
            score=900,
            level_reached=10,
            difficulty="classic",
            enemies_destroyed=20,
            currency_collected=80,
            currency_spent=40,
            date="2026-02-28T12:00:00+00:00",
        ),
    ]
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    how_to_play = HowToPlayState(_MachineStub())
    rows = how_to_play._build_controls_text()
    assert any(row.startswith("Fire::") for row in rows)
    assert any(row.startswith("Pause/Back::") for row in rows)

    high_scores = HighScoresState(_MachineStub())
    high_scores.on_enter()
    assert [entry.score for entry in high_scores._scores] == [900, 500]
    high_scores._current_filter = "hard"
    assert [entry.name for entry in high_scores._filtered_scores()] == ["AAA"]
