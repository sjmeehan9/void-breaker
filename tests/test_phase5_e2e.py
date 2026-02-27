"""Phase 5 end-to-end flow integration test."""

from __future__ import annotations

from types import SimpleNamespace

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings, HighScoreEntry
from asterax.app.src.states.combat import CombatPhaseState
from asterax.app.src.states.game_over import GameOverPhase, GameOverState
from asterax.app.src.states.main_menu import MainMenuState
from asterax.app.src.states.state_machine import StateMachine


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

    def save_high_scores(self, entries: list[HighScoreEntry]) -> None:
        self._scores = list(entries)


def test_phase5_full_loop_e2e_flow(monkeypatch) -> None:
    """Simulate menu->combat->shop cadence->death->name entry->leaderboard save."""
    persistence = _PersistenceStub()
    window = SimpleNamespace(
        width=1280,
        height=960,
        input_manager=InputManager(GameSettings()),
        audio_manager=SimpleNamespace(
            play=lambda _: None,
            play_level_clear=lambda: None,
            play_hit=lambda: None,
            play_enemy_explode=lambda: None,
            play_fire=lambda: None,
        ),
        persistence=persistence,
        runtime_settings=persistence.load_settings(),
        trigger_screen_shake=lambda _: None,
    )
    monkeypatch.setattr(arcade, "get_window", lambda: window)

    machine = StateMachine()
    machine.switch_state(MainMenuState(machine))
    menu_state = machine.current_state
    assert isinstance(menu_state, MainMenuState)

    menu_state.on_key_press(arcade.key.ENTER, 0)
    menu_state.on_key_press(arcade.key.ENTER, 0)
    menu_state.on_update(1.0)
    assert isinstance(machine.current_state, CombatPhaseState)

    combat = machine.current_state
    assert isinstance(combat, CombatPhaseState)
    shop_transitions: list[str] = []
    combat.state_machine = SimpleNamespace(
        switch_state=lambda state: shop_transitions.append(type(state).__name__)
    )
    for _ in range(5):
        combat._transition_to_shop()
        combat._advance_level()
    assert shop_transitions.count("ShopPhaseState") == 5

    game_over = GameOverState(
        state_machine=SimpleNamespace(switch_state=lambda _: None),
        run_stats={"score": 4321, "level_reached": 6},
        persistence=persistence,
        is_practice=False,
    )
    game_over.on_enter()
    game_over._summary_elapsed_seconds = game_over._summary_min_seconds  # noqa: SLF001
    game_over.on_key_press(arcade.key.ENTER, 0)
    assert game_over._phase is GameOverPhase.NAME_ENTRY  # noqa: SLF001

    for key in (arcade.key.A, arcade.key.B, arcade.key.C):
        game_over.on_key_press(key, 0)
    game_over.on_key_press(arcade.key.ENTER, 0)

    assert any(
        entry.name == "ABC" and entry.score == 4321 for entry in persistence._scores
    )
