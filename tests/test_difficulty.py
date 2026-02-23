"""Phase 3 procedural difficulty progression tests."""

from __future__ import annotations

from asterax.app.src.config.difficulty_tables import get_difficulty_params


def test_difficulty_scaling_levels_1_to_30() -> None:
    """Difficulty parameters should remain valid and progressively tougher."""
    asteroid_counts: list[int] = []
    asteroid_speed_max_values: list[float] = []

    for level in range(1, 31):
        params = get_difficulty_params(level)
        asteroid_counts.append(params.asteroid_count)
        asteroid_speed_max_values.append(params.asteroid_speed_max)
        assert params.asteroid_count >= 1
        assert params.asteroid_speed_min >= 0.0
        assert params.asteroid_speed_max >= params.asteroid_speed_min
        # Phase 3: Enemy spawning enabled from level 6+
        if level < 6:
            assert params.enemy_spawn_enabled is False
            assert params.enemy_count_max == 0
        else:
            assert params.enemy_spawn_enabled is True
            assert params.enemy_count_max > 0
            assert params.enemy_spawn_interval > 0.0
            assert 0.0 <= params.aggressive_ratio <= 1.0
            assert 0.0 <= params.enemy_aggression <= 1.0

    assert asteroid_counts == sorted(asteroid_counts)
    assert asteroid_speed_max_values == sorted(asteroid_speed_max_values)
