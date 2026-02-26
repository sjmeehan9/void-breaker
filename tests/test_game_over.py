"""Tests for the Phase 5.5 game-over flow and high-score entry."""

from __future__ import annotations

from types import SimpleNamespace

import arcade
import pytest
from asterax.app.src.persistence.schemas import GameSettings, HighScoreEntry
from asterax.app.src.states.game_over import GameOverPhase, GameOverState


class _FakePersistence:
    """Persistence test double capturing read/write interactions."""

    def __init__(
        self,
        high_scores: list[HighScoreEntry] | None = None,
        settings: GameSettings | None = None,
    ) -> None:
        self._high_scores = list(high_scores or [])
        self._settings = settings or GameSettings()
        self.saved_entries: list[HighScoreEntry] | None = None

    def load_high_scores(self) -> list[HighScoreEntry]:
        """Return configured high-score entries."""
        return list(self._high_scores)

    def save_high_scores(self, entries: list[HighScoreEntry]) -> None:
        """Capture persisted high-score payload."""
        self.saved_entries = list(entries)

    def load_settings(self) -> GameSettings:
        """Return configured settings for difficulty propagation."""
        return self._settings


def _entry(score: int) -> HighScoreEntry:
    """Create a concise high-score record for tests."""
    return HighScoreEntry(
        name="ABC",
        score=score,
        level_reached=3,
        difficulty="classic",
        enemies_destroyed=1,
        currency_collected=10,
        currency_spent=4,
        date="2026-02-27T00:00:00+00:00",
    )


def test_check_qualification_true_when_fewer_than_ten_entries() -> None:
    """Scores should always qualify while leaderboard has fewer than 10 rows."""
    state = GameOverState(state_machine=SimpleNamespace(), run_stats={"score": 10})

    assert state._check_qualification([_entry(100), _entry(90)]) is True  # noqa: SLF001


def test_check_qualification_compares_against_tenth_score() -> None:
    """Qualification should depend on strict top-10 cutoff."""
    state = GameOverState(state_machine=SimpleNamespace(), run_stats={"score": 105})
    state.run_summary.score = 105
    scores = [
        _entry(score) for score in [200, 190, 180, 170, 160, 150, 140, 130, 120, 100]
    ]

    assert state._check_qualification(scores) is True  # noqa: SLF001

    state_equal = GameOverState(
        state_machine=SimpleNamespace(), run_stats={"score": 100}
    )
    state_equal.run_summary.score = 100
    assert state_equal._check_qualification(scores) is False  # noqa: SLF001


def test_name_entry_only_accepts_alphanumeric_and_caps_length() -> None:
    """Name buffer should reject non-alphanumeric keys and limit to 10 chars."""
    state = GameOverState(state_machine=SimpleNamespace())
    state._phase = GameOverPhase.NAME_ENTRY  # noqa: SLF001

    for key in [
        arcade.key.A,
        arcade.key.SPACE,
        arcade.key.SLASH,
        arcade.key.KEY_1,
        arcade.key.B,
        arcade.key.C,
        arcade.key.D,
        arcade.key.E,
        arcade.key.F,
        arcade.key.G,
        arcade.key.H,
        arcade.key.I,
        arcade.key.J,
    ]:
        state.on_key_press(key, 0)

    assert state._name_buffer == "A1BCDEFGHI"  # noqa: SLF001


def test_submit_high_score_populates_expected_fields(monkeypatch) -> None:
    """Submitting a valid name should persist a fully populated high-score entry."""
    settings = GameSettings(difficulty="hard")
    persistence = _FakePersistence(high_scores=[_entry(400)], settings=settings)
    state = GameOverState(
        state_machine=SimpleNamespace(),
        run_stats={
            "score": 500,
            "level_reached": 8,
            "enemies_destroyed": 11,
            "currency_collected": 77,
            "currency_spent": 35,
        },
        persistence=persistence,
    )
    monkeypatch.setattr(
        "asterax.app.src.states.game_over.arcade.get_window",
        lambda: SimpleNamespace(audio_manager=SimpleNamespace(play=lambda _: None)),
    )

    state.on_enter()
    state._phase = GameOverPhase.NAME_ENTRY  # noqa: SLF001
    state._name_buffer = "ACE"  # noqa: SLF001

    assert state._submit_high_score() is True  # noqa: SLF001
    assert persistence.saved_entries is not None
    saved = persistence.saved_entries[0]
    assert saved.name == "ACE"
    assert saved.score == 500
    assert saved.level_reached == 8
    assert saved.difficulty == "hard"
    assert saved.enemies_destroyed == 11
    assert saved.currency_collected == 77
    assert saved.currency_spent == 35
    assert "T" in saved.date


def test_on_enter_hydrates_run_summary_fields(monkeypatch) -> None:
    """Run-summary payload should map to the renderable summary model."""
    persistence = _FakePersistence(high_scores=[])
    state = GameOverState(
        state_machine=SimpleNamespace(),
        run_stats={
            "score": 1234,
            "level_reached": 12,
            "enemies_destroyed": 17,
            "asteroids_destroyed": 48,
            "currency_collected": 200,
            "currency_spent": 150,
            "insurance_tier": "premium",
        },
        persistence=persistence,
    )
    monkeypatch.setattr(
        "asterax.app.src.states.game_over.arcade.get_window",
        lambda: SimpleNamespace(audio_manager=SimpleNamespace(play=lambda _: None)),
    )

    state.on_enter()

    assert state.run_summary.score == 1234
    assert state.run_summary.level_reached == 12
    assert state.run_summary.enemies_destroyed == 17
    assert state.run_summary.asteroids_destroyed == 48
    assert state.run_summary.currency_collected == 200
    assert state.run_summary.currency_spent == 150
    assert state.run_summary.insurance_tier == "premium"
