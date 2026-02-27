"""Phase 5 game-over flow coverage tests."""

from __future__ import annotations

from types import SimpleNamespace

import arcade
from asterax.app.src.persistence.schemas import GameSettings, HighScoreEntry
from asterax.app.src.states.game_over import GameOverPhase, GameOverState


class _PersistenceStub:
    def __init__(self) -> None:
        self.saved_scores: list[HighScoreEntry] | None = None

    def load_high_scores(self) -> list[HighScoreEntry]:
        return []

    def save_high_scores(self, entries: list[HighScoreEntry]) -> None:
        self.saved_scores = entries

    def load_settings(self) -> GameSettings:
        return GameSettings(difficulty="hard")


def test_game_over_name_entry_and_practice_skip(monkeypatch) -> None:
    """Normal game-over allows name entry, while practice skips leaderboard flow."""
    persistence = _PersistenceStub()
    window = SimpleNamespace(
        persistence=persistence,
        input_manager=SimpleNamespace(get_binding=lambda _: arcade.key.ESCAPE),
        audio_manager=SimpleNamespace(play=lambda _: None),
    )
    monkeypatch.setattr(arcade, "get_window", lambda: window)

    state = GameOverState(
        state_machine=SimpleNamespace(switch_state=lambda _: None),
        run_stats={"score": 2222, "level_reached": 9},
        persistence=persistence,
    )
    state.on_enter()
    state._summary_elapsed_seconds = state._summary_min_seconds
    state.on_key_press(arcade.key.ENTER, 0)
    assert state._phase is GameOverPhase.NAME_ENTRY

    for key in (arcade.key.A, arcade.key.B, arcade.key.C):
        state.on_key_press(key, 0)
    state.on_key_press(arcade.key.ENTER, 0)
    assert state._phase is GameOverPhase.OPTIONS
    assert persistence.saved_scores is not None

    practice_state = GameOverState(
        state_machine=SimpleNamespace(switch_state=lambda _: None),
        run_stats={"score": 9999},
        persistence=persistence,
        is_practice=True,
    )
    practice_state.on_enter()
    practice_state._summary_elapsed_seconds = practice_state._summary_min_seconds
    practice_state.on_key_press(arcade.key.ENTER, 0)
    assert practice_state._phase is GameOverPhase.OPTIONS
