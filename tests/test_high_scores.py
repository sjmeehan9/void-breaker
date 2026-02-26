"""Tests for the Phase 5.3 high scores screen."""

from __future__ import annotations

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings, HighScoreEntry
from asterax.app.src.states.high_scores import HighScoresState


class FakePersistence:
    """Persistence test double returning predefined high score entries."""

    def __init__(self, entries: list[HighScoreEntry]) -> None:
        """Store static leaderboard entries for load calls."""
        self._entries = entries

    def load_high_scores(self) -> list[HighScoreEntry]:
        """Return preconfigured entries."""
        return list(self._entries)


class FakeWindow:
    """Window test double for high-scores state tests."""

    def __init__(self, entries: list[HighScoreEntry]) -> None:
        """Set up attributes read by HighScoresState."""
        self.width = 1280
        self.height = 960
        self.input_manager = InputManager(GameSettings())
        self.persistence = FakePersistence(entries)


class RecordingStateMachine:
    """Minimal state machine test double for transition assertions."""

    def __init__(self) -> None:
        """Initialize transition recording storage."""
        self.switched_to: list[str] = []

    def switch_state(self, state: object) -> None:
        """Record class names of switched states."""
        self.switched_to.append(type(state).__name__)


def _entry(name: str, score: int, difficulty: str) -> HighScoreEntry:
    """Create a high score entry for concise test setup."""
    return HighScoreEntry(
        name=name,
        score=score,
        level_reached=5,
        difficulty=difficulty,
        enemies_destroyed=20,
        currency_collected=200,
        currency_spent=100,
        date="2026-02-27T15:30:00",
    )


def test_load_scores_sorts_by_score_descending(monkeypatch) -> None:
    """Loaded entries should be sorted highest-to-lowest by score."""
    window = FakeWindow(
        [
            _entry("LOW", 1000, "classic"),
            _entry("TOP", 5000, "classic"),
            _entry("MID", 2500, "classic"),
        ]
    )
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = HighScoresState(RecordingStateMachine())

    scores = state._load_scores()

    assert [entry.score for entry in scores] == [5000, 2500, 1000]


def test_difficulty_filter_limits_entries(monkeypatch) -> None:
    """Active difficulty filter should only return matching rows."""
    window = FakeWindow(
        [
            _entry("CAS", 3200, "casual"),
            _entry("CLA", 4200, "classic"),
            _entry("HAR", 5100, "hard"),
        ]
    )
    monkeypatch.setattr(arcade, "get_window", lambda: window)
    state = HighScoresState(RecordingStateMachine())
    state.on_enter()

    state._current_filter = "classic"
    filtered = state._filtered_scores()

    assert len(filtered) == 1
    assert filtered[0].difficulty == "classic"
    assert filtered[0].name == "CLA"


def test_empty_leaderboard_produces_no_scores_state(monkeypatch) -> None:
    """An empty persistence payload should produce empty filtered results."""
    monkeypatch.setattr(arcade, "get_window", lambda: FakeWindow([]))
    state = HighScoresState(RecordingStateMachine())
    state.on_enter()

    assert state._filtered_scores() == []
    assert state.NO_SCORES_MESSAGE == "No scores yet -- start a new game!"
