"""Tests for Phase 5.10 practice/training mode behavior."""

from __future__ import annotations

from types import SimpleNamespace

import arcade
import pytest
from asterax.app.src.config.difficulty_tables import get_difficulty_params
from asterax.app.src.config.game_config import DifficultyParams
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.states.combat import CombatPhaseState
from asterax.app.src.states.game_over import GameOverPhase, GameOverState
from asterax.app.src.states.practice_config import PracticeConfigState


class _FakeAudioManager:
    """Lightweight audio manager test double."""

    def __init__(self) -> None:
        """Initialize recorded sounds list."""
        self.played: list[str] = []

    def play(self, sound_name: str) -> None:
        """Record a requested sound playback."""
        self.played.append(sound_name)


class _FakeWindow:
    """Window test double for state-level practice tests."""

    def __init__(self) -> None:
        """Set up attributes needed by practice and game-over states."""
        self.width = 1280
        self.height = 960
        self.audio_manager = _FakeAudioManager()
        self.input_manager = InputManager(GameSettings())
        self.persistence = SimpleNamespace(
            load_settings=lambda: GameSettings(),
            load_high_scores=lambda: [],
            save_high_scores=lambda entries: None,
        )


def _assert_params_equal(left: DifficultyParams, right: DifficultyParams) -> None:
    """Assert two DifficultyParams values are field-wise equal."""
    assert left.asteroid_count == right.asteroid_count
    assert left.asteroid_speed_min == pytest.approx(right.asteroid_speed_min)
    assert left.asteroid_speed_max == pytest.approx(right.asteroid_speed_max)
    assert left.enemy_spawn_enabled is right.enemy_spawn_enabled
    assert left.enemy_count_max == right.enemy_count_max
    assert left.enemy_spawn_interval == pytest.approx(right.enemy_spawn_interval)
    assert left.enemy_aggression == pytest.approx(right.enemy_aggression)
    assert left.aggressive_ratio == pytest.approx(right.aggressive_ratio)
    assert left.currency_drop_chance == pytest.approx(right.currency_drop_chance)
    assert left.currency_value_base == right.currency_value_base


def test_build_practice_params_with_all_toggles_off_returns_level1_defaults(
    monkeypatch,
) -> None:
    """Practice params builder should return Level-1 defaults when toggles are off."""
    monkeypatch.setattr(arcade, "get_window", lambda: _FakeWindow())
    state = PracticeConfigState(SimpleNamespace(switch_state=lambda _: None))
    state._toggles = {
        "asteroids_only": False,
        "infinite_shields": False,
        "reduced_count": False,
    }

    built = state._build_practice_params()
    baseline = get_difficulty_params(1)

    _assert_params_equal(built, baseline)


def test_build_practice_params_with_asteroids_only_disables_enemies(
    monkeypatch,
) -> None:
    """Asteroids-only practice config should disable enemy spawning."""
    monkeypatch.setattr(arcade, "get_window", lambda: _FakeWindow())
    state = PracticeConfigState(SimpleNamespace(switch_state=lambda _: None))
    state._toggles["asteroids_only"] = True

    built = state._build_practice_params()

    assert built.enemy_spawn_enabled is False
    assert built.enemy_count_max == 0
    assert built.enemy_aggression == pytest.approx(0.0)


def test_build_practice_params_with_reduced_count_halves_asteroids(monkeypatch) -> None:
    """Reduced-count toggle should halve level asteroid count with floor of one."""
    monkeypatch.setattr(arcade, "get_window", lambda: _FakeWindow())
    state = PracticeConfigState(SimpleNamespace(switch_state=lambda _: None))
    state._toggles = {
        "asteroids_only": False,
        "infinite_shields": False,
        "reduced_count": True,
    }

    built = state._build_practice_params()

    assert built.asteroid_count == 2


def test_combat_practice_game_over_uses_practice_flag() -> None:
    """Practice combat should route game-over with `is_practice=True`."""

    class _Machine:
        def __init__(self) -> None:
            self.switched_to = None

        def switch_state(self, state: object) -> None:
            self.switched_to = state

    machine = _Machine()
    state = CombatPhaseState(
        state_machine=machine,  # type: ignore[arg-type]
        is_practice=True,
    )

    state._trigger_game_over(persistence=SimpleNamespace())

    assert isinstance(machine.switched_to, GameOverState)
    assert machine.switched_to._is_practice is True  # noqa: SLF001


def test_game_over_practice_skips_name_entry(monkeypatch) -> None:
    """Practice game-over should jump from summary directly to options phase."""
    monkeypatch.setattr(arcade, "get_window", lambda: _FakeWindow())
    state = GameOverState(
        state_machine=SimpleNamespace(switch_state=lambda _: None),
        run_stats={"score": 999},
        persistence=SimpleNamespace(
            load_high_scores=lambda: [],
            load_settings=lambda: GameSettings(),
            save_high_scores=lambda entries: None,
        ),
        is_practice=True,
    )
    state.on_enter()
    state._summary_elapsed_seconds = state._summary_min_seconds  # noqa: SLF001

    state.on_key_press(arcade.key.ENTER, 0)

    assert state._phase is GameOverPhase.OPTIONS  # noqa: SLF001
    assert state._qualifies_for_leaderboard is False  # noqa: SLF001
