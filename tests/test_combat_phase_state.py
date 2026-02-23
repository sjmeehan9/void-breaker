"""Focused tests for combat phase progression and game-over flow."""

from __future__ import annotations

from types import SimpleNamespace

import asterax.app.src.states.combat as combat_module
import asterax.app.src.states.game_over as game_over_module
import pytest
from asterax.app.src.states.combat import CombatPhaseState
from asterax.app.src.states.game_over import GameOverState


def test_combat_on_update_uses_fixed_timestep_accumulator(monkeypatch) -> None:
    """on_update should run deterministic physics steps based on fixed dt."""
    state = CombatPhaseState(state_machine=SimpleNamespace())
    state.physics_engine = object()

    step_calls: list[float] = []
    monkeypatch.setattr(state, "_physics_step", lambda dt: step_calls.append(dt))

    state.on_update(combat_module.PHYSICS_DT * 2.5)

    assert len(step_calls) == 2
    assert state.accumulator == pytest.approx(combat_module.PHYSICS_DT * 0.5)


def test_check_level_clear_advances_when_asteroids_empty(monkeypatch) -> None:
    """Level-clear check should advance only when no asteroids remain."""
    state = CombatPhaseState(state_machine=SimpleNamespace())
    state.entity_manager.asteroids = []  # type: ignore[assignment]

    advanced: list[bool] = []
    monkeypatch.setattr(state, "_advance_level", lambda: advanced.append(True))

    state._check_level_clear()

    assert advanced == [True]


def test_advance_level_resets_and_spawns(monkeypatch) -> None:
    """Advancing the level should clear transient entities and spawn next wave."""
    state = CombatPhaseState(state_machine=SimpleNamespace())
    ship = SimpleNamespace(
        center_x=10.0,
        center_y=20.0,
        velocity_x=3.0,
        velocity_y=4.0,
        shields=100.0,
        max_shields=100.0,
    )
    state.entity_manager.player_ship = ship  # type: ignore[assignment]
    state.entity_manager.player_projectiles = [1, 2]  # type: ignore[assignment]
    state.entity_manager.currency_pickups = [1]  # type: ignore[assignment]
    state.entity_manager.asteroids = []  # type: ignore[assignment]

    spawned = [SimpleNamespace(velocity_x=400.0, velocity_y=-410.0)]
    state.spawn_manager = SimpleNamespace(
        spawn_level_asteroids=lambda **kwargs: spawned,
        reset_enemy_spawning=lambda: None,
    )  # type: ignore[assignment]
    state.entity_manager.clear_projectiles = lambda: state.entity_manager.player_projectiles.clear()  # type: ignore[method-assign]
    state.hud = None
    state._sync_state_for_hud = lambda: None  # type: ignore[method-assign]

    audio_calls: list[str] = []
    monkeypatch.setattr(
        combat_module.arcade,
        "get_window",
        lambda: SimpleNamespace(
            width=1280,
            height=960,
            audio_manager=SimpleNamespace(play=lambda name: audio_calls.append(name)),
        ),
    )

    state._advance_level()

    assert state.current_level == 2
    assert state.entity_manager.player_projectiles == []
    assert state.entity_manager.currency_pickups == []
    assert state.entity_manager.asteroids == spawned
    assert ship.center_x == 640.0
    assert ship.center_y == 480.0
    assert ship.velocity_x == 0.0
    assert ship.velocity_y == 0.0
    assert audio_calls == ["level_clear"]


def test_trigger_game_over_switches_with_run_stats() -> None:
    """Game-over transition should include score, level, and currency summary."""

    class FakeMachine:
        def __init__(self) -> None:
            self.switched_to = None

        def switch_state(self, state: object) -> None:
            self.switched_to = state

    machine = FakeMachine()
    state = CombatPhaseState(state_machine=machine)  # type: ignore[arg-type]
    state.current_level = 4
    state.score_manager.score = 1234
    state.currency_manager.earn(70)
    assert state.currency_manager.spend(10)

    state._trigger_game_over(persistence=SimpleNamespace())

    assert isinstance(machine.switched_to, GameOverState)
    assert machine.switched_to._run_stats_payload["score"] == 1234  # noqa: SLF001
    assert machine.switched_to._run_stats_payload["level_reached"] == 4  # noqa: SLF001
    assert (
        machine.switched_to._run_stats_payload["currency_collected"] == 70
    )  # noqa: SLF001
    assert (
        machine.switched_to._run_stats_payload["currency_spent"] == 10
    )  # noqa: SLF001


def test_physics_step_delays_game_over_for_destruction_sequence(monkeypatch) -> None:
    """Shields reaching zero should delay game-over transition by 0.8s."""
    state = CombatPhaseState(state_machine=SimpleNamespace())
    ship = SimpleNamespace(
        center_x=100.0,
        center_y=120.0,
        velocity_x=0.0,
        velocity_y=0.0,
        shields=0.0,
        max_shields=100.0,
        update_invulnerability=lambda dt: None,
    )
    state.entity_manager.player_ship = ship  # type: ignore[assignment]
    state.physics_engine = SimpleNamespace(update=lambda **kwargs: None)  # type: ignore[assignment]
    state._check_level_clear = lambda: None  # type: ignore[method-assign]
    state._spawn_enemies = lambda **kwargs: None  # type: ignore[method-assign]
    state._update_enemies = lambda **kwargs: None  # type: ignore[method-assign]
    state._process_enemy_collisions = lambda **kwargs: None  # type: ignore[method-assign]
    state.collision_system = SimpleNamespace(check_all=lambda **kwargs: None)  # type: ignore[assignment]
    state.particle_system = SimpleNamespace(update=lambda dt: None)  # type: ignore[assignment]
    state.damage_effects = SimpleNamespace(
        update=lambda dt: None, trigger_destruction_sequence=lambda *args: None
    )  # type: ignore[assignment]
    triggered: list[bool] = []
    state._trigger_game_over = lambda persistence: triggered.append(True)  # type: ignore[method-assign]
    monkeypatch.setattr(
        combat_module.arcade,
        "get_window",
        lambda: SimpleNamespace(
            width=1280,
            height=960,
            input_manager=SimpleNamespace(keys_held=set()),
            audio_manager=SimpleNamespace(play=lambda name: None),
            persistence=SimpleNamespace(),
        ),
    )

    state._physics_step(0.1)
    state._physics_step(0.71)

    assert triggered == [True]


def test_game_over_saves_high_score_when_qualifying(monkeypatch) -> None:
    """Qualifying scores should be persisted with fallback initials."""

    class FakePersistence:
        def __init__(self) -> None:
            self.saved_entries = []

        def load_high_scores(self):
            return []

        def save_high_scores(self, entries):
            self.saved_entries = entries

    monkeypatch.setattr(
        game_over_module.arcade,
        "get_window",
        lambda: SimpleNamespace(persistence=FakePersistence()),
    )
    persistence = FakePersistence()
    state = GameOverState(
        state_machine=SimpleNamespace(),
        run_stats={"score": 999, "level_reached": 3, "currency_collected": 40},
        persistence=persistence,
    )

    state.on_enter()

    assert state.is_high_score is True
    assert len(persistence.saved_entries) == 1
    assert persistence.saved_entries[0].name == "AAA"
    assert persistence.saved_entries[0].score == 999


def test_combat_multi_level_session_with_enemy_updates_no_crash(monkeypatch) -> None:
    """Simulate multi-level combat progression and verify enemy systems stay stable."""

    class _InputStub:
        def __init__(self) -> None:
            self.keys_held: set[int] = set()

        def is_action_held(self, action: str) -> bool:
            del action
            return False

    window = SimpleNamespace(
        width=1280,
        height=960,
        input_manager=_InputStub(),
        audio_manager=SimpleNamespace(play=lambda name: None),
        persistence=SimpleNamespace(),
    )
    monkeypatch.setattr(combat_module.arcade, "get_window", lambda: window)
    state = CombatPhaseState(state_machine=SimpleNamespace())
    state.on_enter()
    state.collision_system = SimpleNamespace(check_all=lambda **kwargs: None)  # type: ignore[assignment]
    state._process_enemy_collisions = lambda **kwargs: None  # type: ignore[method-assign]

    for _ in range(14):
        state.entity_manager.asteroids.clear()
        state._physics_step(combat_module.PHYSICS_DT)

    assert state.current_level == 15

    enemy_activity_samples = 0
    for _ in range(int(12.0 / combat_module.PHYSICS_DT)):
        state._physics_step(combat_module.PHYSICS_DT)
        enemy_activity_samples += len(state.entity_manager.enemies)
        enemy_activity_samples += len(state.entity_manager.enemy_projectiles)

    assert enemy_activity_samples > 0
    assert state._game_over_triggered is False  # noqa: SLF001
