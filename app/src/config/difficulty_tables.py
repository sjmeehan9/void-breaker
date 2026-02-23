"""Tiered difficulty scaling definitions."""

from __future__ import annotations

from asterax.app.src.config.game_config import DifficultyParams


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a floating-point value to a closed interval."""

    return max(minimum, min(value, maximum))


DIFFICULTY_TIERS: dict[int, DifficultyParams] = {
    1: DifficultyParams(
        asteroid_count=3,
        asteroid_speed_min=30.0,
        asteroid_speed_max=80.0,
        enemy_spawn_enabled=False,
        enemy_count_max=0,
        enemy_spawn_interval=99.0,
        enemy_aggression=0.0,
        aggressive_ratio=0.0,
        currency_drop_chance=0.4,
        currency_value_base=10,
    ),
    5: DifficultyParams(
        asteroid_count=8,
        asteroid_speed_min=40.0,
        asteroid_speed_max=120.0,
        enemy_spawn_enabled=False,
        enemy_count_max=0,
        enemy_spawn_interval=99.0,
        enemy_aggression=0.0,
        aggressive_ratio=0.0,
        currency_drop_chance=0.4,
        currency_value_base=12,
    ),
    10: DifficultyParams(
        asteroid_count=12,
        asteroid_speed_min=50.0,
        asteroid_speed_max=160.0,
        enemy_spawn_enabled=True,
        enemy_count_max=3,
        enemy_spawn_interval=6.0,
        enemy_aggression=0.4,
        aggressive_ratio=0.2,
        currency_drop_chance=0.35,
        currency_value_base=15,
    ),
    15: DifficultyParams(
        asteroid_count=18,
        asteroid_speed_min=60.0,
        asteroid_speed_max=200.0,
        enemy_spawn_enabled=True,
        enemy_count_max=5,
        enemy_spawn_interval=4.5,
        enemy_aggression=0.6,
        aggressive_ratio=0.4,
        currency_drop_chance=0.35,
        currency_value_base=18,
    ),
    20: DifficultyParams(
        asteroid_count=22,
        asteroid_speed_min=70.0,
        asteroid_speed_max=230.0,
        enemy_spawn_enabled=True,
        enemy_count_max=6,
        enemy_spawn_interval=3.5,
        enemy_aggression=0.75,
        aggressive_ratio=0.55,
        currency_drop_chance=0.3,
        currency_value_base=22,
    ),
    25: DifficultyParams(
        asteroid_count=27,
        asteroid_speed_min=75.0,
        asteroid_speed_max=250.0,
        enemy_spawn_enabled=True,
        enemy_count_max=7,
        enemy_spawn_interval=3.0,
        enemy_aggression=0.85,
        aggressive_ratio=0.65,
        currency_drop_chance=0.3,
        currency_value_base=25,
    ),
    30: DifficultyParams(
        asteroid_count=30,
        asteroid_speed_min=80.0,
        asteroid_speed_max=270.0,
        enemy_spawn_enabled=True,
        enemy_count_max=8,
        enemy_spawn_interval=2.5,
        enemy_aggression=0.9,
        aggressive_ratio=0.7,
        currency_drop_chance=0.28,
        currency_value_base=28,
    ),
}

TIER_LEVELS = tuple(sorted(DIFFICULTY_TIERS.keys()))


def _interpolate(
    start_value: float,
    end_value: float,
    progress: float,
) -> float:
    """Linearly interpolate two scalar values."""

    return start_value + (end_value - start_value) * progress


def _clone_params(params: DifficultyParams) -> DifficultyParams:
    """Return a copy of difficulty parameters."""

    return DifficultyParams(
        asteroid_count=params.asteroid_count,
        asteroid_speed_min=params.asteroid_speed_min,
        asteroid_speed_max=params.asteroid_speed_max,
        enemy_spawn_enabled=params.enemy_spawn_enabled,
        enemy_count_max=params.enemy_count_max,
        enemy_spawn_interval=params.enemy_spawn_interval,
        enemy_aggression=params.enemy_aggression,
        aggressive_ratio=params.aggressive_ratio,
        currency_drop_chance=params.currency_drop_chance,
        currency_value_base=params.currency_value_base,
    )


def _interpolate_params(
    level: int,
    tier_start: int,
    tier_end: int,
    start_params: DifficultyParams,
    end_params: DifficultyParams,
) -> DifficultyParams:
    """Interpolate numeric DifficultyParams fields between two tier boundaries."""

    progress = (level - tier_start) / (tier_end - tier_start)
    enemy_progress = progress
    enemy_count_start = float(start_params.enemy_count_max)
    enemy_spawn_interval_start = start_params.enemy_spawn_interval
    enemy_aggression_start = start_params.enemy_aggression
    aggressive_ratio_start = start_params.aggressive_ratio
    enemy_spawn_enabled = (
        start_params.enemy_spawn_enabled or end_params.enemy_spawn_enabled
    )

    if (
        level >= 6
        and not start_params.enemy_spawn_enabled
        and end_params.enemy_spawn_enabled
    ):
        enemy_count_start = 1.0
        enemy_spawn_interval_start = 8.0
        enemy_aggression_start = 0.3
        aggressive_ratio_start = 0.0
        enemy_progress = _clamp((level - 6) / (tier_end - 6), 0.0, 1.0)

    return DifficultyParams(
        asteroid_count=int(
            round(
                _interpolate(
                    float(start_params.asteroid_count),
                    float(end_params.asteroid_count),
                    progress,
                )
            )
        ),
        asteroid_speed_min=_interpolate(
            start_params.asteroid_speed_min,
            end_params.asteroid_speed_min,
            progress,
        ),
        asteroid_speed_max=_interpolate(
            start_params.asteroid_speed_max,
            end_params.asteroid_speed_max,
            progress,
        ),
        enemy_spawn_enabled=enemy_spawn_enabled and level >= 6,
        enemy_count_max=int(
            round(
                _interpolate(
                    enemy_count_start,
                    float(end_params.enemy_count_max),
                    enemy_progress,
                )
            )
        ),
        enemy_spawn_interval=_interpolate(
            enemy_spawn_interval_start,
            end_params.enemy_spawn_interval,
            enemy_progress,
        ),
        enemy_aggression=_interpolate(
            enemy_aggression_start,
            end_params.enemy_aggression,
            enemy_progress,
        ),
        aggressive_ratio=_interpolate(
            aggressive_ratio_start,
            end_params.aggressive_ratio,
            enemy_progress,
        ),
        currency_drop_chance=_interpolate(
            start_params.currency_drop_chance,
            end_params.currency_drop_chance,
            progress,
        ),
        currency_value_base=int(
            round(
                _interpolate(
                    float(start_params.currency_value_base),
                    float(end_params.currency_value_base),
                    progress,
                )
            )
        ),
    )


def get_difficulty_params(level: int) -> DifficultyParams:
    """Compute interpolated Phase 3 difficulty parameters with a level-30 cap."""

    safe_level = int(_clamp(float(level), 1.0, float(TIER_LEVELS[-1])))

    if safe_level in DIFFICULTY_TIERS:
        return _clone_params(DIFFICULTY_TIERS[safe_level])

    for index, start_level in enumerate(TIER_LEVELS[:-1]):
        end_level = TIER_LEVELS[index + 1]
        if start_level < safe_level < end_level:
            return _interpolate_params(
                level=safe_level,
                tier_start=start_level,
                tier_end=end_level,
                start_params=DIFFICULTY_TIERS[start_level],
                end_params=DIFFICULTY_TIERS[end_level],
            )

    return _clone_params(DIFFICULTY_TIERS[TIER_LEVELS[-1]])


def get_difficulty(level: int, base: str = "classic") -> DifficultyParams:
    """Compute procedural difficulty parameters for a level and base mode."""

    base_params = get_difficulty_params(level)

    if base == "classic":
        asteroid_multiplier = 1.0
        currency_multiplier = 1.0
    elif base == "casual":
        asteroid_multiplier = 0.7
        currency_multiplier = 1.3
    elif base == "hard":
        asteroid_multiplier = 1.3
        currency_multiplier = 0.7
    else:
        raise ValueError(f"Unknown difficulty base '{base}'")

    adjusted_asteroid_count = int(
        round(_clamp(base_params.asteroid_count * asteroid_multiplier, 1.0, 30.0))
    )
    adjusted_currency_drop_chance = _clamp(
        base_params.currency_drop_chance * currency_multiplier,
        0.05,
        1.0,
    )

    return DifficultyParams(
        asteroid_count=adjusted_asteroid_count,
        asteroid_speed_min=base_params.asteroid_speed_min,
        asteroid_speed_max=base_params.asteroid_speed_max,
        enemy_spawn_enabled=base_params.enemy_spawn_enabled,
        enemy_count_max=base_params.enemy_count_max,
        enemy_spawn_interval=base_params.enemy_spawn_interval,
        enemy_aggression=base_params.enemy_aggression,
        aggressive_ratio=base_params.aggressive_ratio,
        currency_drop_chance=adjusted_currency_drop_chance,
        currency_value_base=base_params.currency_value_base,
    )
