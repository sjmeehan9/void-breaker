"""Phase 5 practice-mode behavior coverage tests."""

from __future__ import annotations

from types import SimpleNamespace

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.states.combat import CombatPhaseState
from asterax.app.src.states.game_over import GameOverPhase, GameOverState
from asterax.app.src.states.practice_config import PracticeConfigState


class _WindowStub:
    def __init__(self) -> None:
        self.width = 1280
        self.height = 960
        self.audio_manager = SimpleNamespace(play=lambda _: None)
        self.persistence = SimpleNamespace(
            load_settings=lambda: GameSettings(),
            load_high_scores=lambda: [],
            save_high_scores=lambda _: None,
        )
        self.input_manager = InputManager(GameSettings())


def test_practice_params_and_practice_game_over_flow(monkeypatch) -> None:
    """Practice params apply toggles and practice game-over skips leaderboard entry."""
    monkeypatch.setattr(arcade, "get_window", lambda: _WindowStub())

    config_state = PracticeConfigState(SimpleNamespace(switch_state=lambda _: None))
    config_state._toggles = {
        "asteroids_only": True,
        "infinite_shields": True,
        "reduced_count": True,
    }
    params = config_state._build_practice_params()
    assert params.enemy_spawn_enabled is False
    assert params.asteroid_count >= 1

    machine = SimpleNamespace(switched_to=None)
    machine.switch_state = lambda state: setattr(machine, "switched_to", state)
    combat = CombatPhaseState(machine, is_practice=True)
    combat._trigger_game_over(SimpleNamespace())
    assert isinstance(machine.switched_to, GameOverState)
    assert machine.switched_to._is_practice is True  # noqa: SLF001

    game_over = GameOverState(
        state_machine=SimpleNamespace(switch_state=lambda _: None),
        run_stats={"score": 100},
        persistence=SimpleNamespace(
            load_high_scores=lambda: [],
            load_settings=lambda: GameSettings(),
            save_high_scores=lambda _: None,
        ),
        is_practice=True,
    )
    game_over.on_enter()
    game_over._summary_elapsed_seconds = game_over._summary_min_seconds  # noqa: SLF001
    game_over.on_key_press(arcade.key.ENTER, 0)
    assert game_over._phase is GameOverPhase.OPTIONS  # noqa: SLF001
