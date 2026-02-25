"""Tiered Phase 3 difficulty progression tests."""

from __future__ import annotations

import pytest
from asterax.app.src.config.difficulty_tables import get_difficulty_params


def test_get_difficulty_params_level_1_values() -> None:
    """Level 1 parameters should match the first tier exactly."""
    level_one = get_difficulty_params(1)

    assert level_one.asteroid_count == 3
    assert level_one.asteroid_speed_min == 30.0
    assert level_one.asteroid_speed_max == 80.0
    assert level_one.enemy_spawn_enabled is False
    assert level_one.enemy_count_max == 0
    assert level_one.enemy_spawn_interval == 99.0
    assert level_one.currency_drop_chance == 0.4
    assert level_one.currency_value_base == 10


def test_get_difficulty_params_level_30_values() -> None:
    """Level 30 parameters should match the final tier exactly."""
    level_thirty = get_difficulty_params(30)

    assert level_thirty.asteroid_count == 30
    assert level_thirty.asteroid_speed_min == 80.0
    assert level_thirty.asteroid_speed_max == 270.0
    assert level_thirty.enemy_spawn_enabled is True
    assert level_thirty.enemy_count_max == 8
    assert level_thirty.enemy_spawn_interval == 2.5
    assert level_thirty.enemy_aggression == 0.9
    assert level_thirty.aggressive_ratio == 0.7
    assert level_thirty.currency_drop_chance == 0.28
    assert level_thirty.currency_value_base == 28


def test_get_difficulty_params_level_7_is_interpolated() -> None:
    """Level 7 should interpolate between level-5 and level-10 tiers."""
    level_seven = get_difficulty_params(7)

    assert level_seven.asteroid_count == 10
    assert level_seven.asteroid_speed_min == 44.0
    assert level_seven.asteroid_speed_max == 136.0
    assert level_seven.enemy_spawn_enabled is True
    assert level_seven.enemy_count_max == 2
    assert level_seven.enemy_spawn_interval == pytest.approx(7.5)
    assert level_seven.enemy_aggression == pytest.approx(0.325)
    assert level_seven.aggressive_ratio == pytest.approx(0.05)
    assert level_seven.currency_drop_chance == pytest.approx(0.38)
    assert level_seven.currency_value_base == 13


def test_enemy_spawning_threshold() -> None:
    """Enemy spawning should be disabled through level 5 and enabled at level 6+."""
    assert get_difficulty_params(5).enemy_spawn_enabled is False
    assert get_difficulty_params(6).enemy_spawn_enabled is True


def test_difficulty_caps_after_level_30() -> None:
    """Levels above 30 should clamp to level-30 parameters."""
    assert get_difficulty_params(50) == get_difficulty_params(30)


def test_asteroid_count_is_monotonic_levels_1_to_30() -> None:
    """Asteroid count should not decrease over levels 1 to 30."""
    asteroid_counts = [
        get_difficulty_params(level).asteroid_count for level in range(1, 31)
    ]
    assert asteroid_counts == sorted(asteroid_counts)


def test_enemy_count_is_monotonic_levels_6_to_30() -> None:
    """Enemy cap should not decrease over levels 6 to 30."""
    enemy_counts = [
        get_difficulty_params(level).enemy_count_max for level in range(6, 31)
    ]
    assert enemy_counts == sorted(enemy_counts)


def test_difficulty_values_are_in_expected_bounds() -> None:
    """All generated values should remain in documented ranges."""
    for level in range(1, 51):
        params = get_difficulty_params(level)
        assert 3 <= params.asteroid_count <= 30
        assert 30.0 <= params.asteroid_speed_min <= 80.0
        assert params.asteroid_speed_min <= params.asteroid_speed_max <= 270.0
        assert 0 <= params.enemy_count_max <= 8
        assert 2.5 <= params.enemy_spawn_interval <= 99.0
        assert 0.0 <= params.enemy_aggression <= 0.9
        assert 0.0 <= params.aggressive_ratio <= 0.7
        assert 0.28 <= params.currency_drop_chance <= 0.4
        assert 10 <= params.currency_value_base <= 28
