"""Procedural difficulty scaling definitions."""

from __future__ import annotations

from asterax.app.src.config.game_config import DifficultyParams


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a floating-point value to a closed interval."""

    return max(minimum, min(value, maximum))


def get_difficulty(level: int, base: str = "classic") -> DifficultyParams:
    """Compute procedural difficulty parameters for a level and base mode."""

    safe_level = max(1, level)

    asteroid_count = min(20.0, 4.0 + (safe_level - 1))
    asteroid_speed_min = min(200.0, 50.0 + (safe_level - 1) * 5.0)
    asteroid_speed_max = min(400.0, 150.0 + (safe_level - 1) * 8.0)
    enemy_spawn_enabled = safe_level >= 6
    enemy_count_max = min(10, 1 + ((safe_level - 6) // 3)) if enemy_spawn_enabled else 0
    enemy_spawn_interval = max(3.0, 10.0 - (safe_level - 1) * 0.3)
    enemy_aggression = min(0.9, 0.2 + (safe_level - 1) * 0.03)
    currency_drop_chance = max(0.2, 0.4 - (safe_level - 1) * 0.005)
    currency_value_base = 10 + (safe_level - 1) * 2

    if base == "classic":
        asteroid_multiplier = 1.0
        aggression_multiplier = 1.0
        currency_multiplier = 1.0
    elif base == "casual":
        asteroid_multiplier = 0.7
        aggression_multiplier = 0.6
        currency_multiplier = 1.3
    elif base == "hard":
        asteroid_multiplier = 1.3
        aggression_multiplier = 1.3
        currency_multiplier = 0.7
    else:
        raise ValueError(f"Unknown difficulty base '{base}'")

    adjusted_asteroid_count = int(
        round(_clamp(asteroid_count * asteroid_multiplier, 1.0, 30.0))
    )
    adjusted_enemy_aggression = _clamp(
        enemy_aggression * aggression_multiplier,
        0.0,
        1.0,
    )
    adjusted_currency_drop_chance = _clamp(
        currency_drop_chance * currency_multiplier,
        0.05,
        1.0,
    )

    return DifficultyParams(
        asteroid_count=adjusted_asteroid_count,
        asteroid_speed_min=asteroid_speed_min,
        asteroid_speed_max=asteroid_speed_max,
        enemy_spawn_enabled=enemy_spawn_enabled,
        enemy_count_max=enemy_count_max,
        enemy_spawn_interval=enemy_spawn_interval,
        enemy_aggression=adjusted_enemy_aggression,
        currency_drop_chance=adjusted_currency_drop_chance,
        currency_value_base=currency_value_base,
    )
