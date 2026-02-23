"""Procedural difficulty scaling definitions."""

from __future__ import annotations

from asterax.app.src.config.game_config import DifficultyParams


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a floating-point value to a closed interval."""

    return max(minimum, min(value, maximum))


def get_difficulty_params(level: int) -> DifficultyParams:
    """Compute Phase 3 difficulty parameters with asteroid and enemy scaling."""

    safe_level = max(1, level)
    speed_growth = 1.1 ** (safe_level - 1)

    # Asteroid parameters (existing Phase 2 logic)
    asteroid_count = int(round(_clamp(4.0 + (safe_level - 1) * 1.2, 4.0, 20.0)))
    asteroid_speed_min = _clamp(50.0 * speed_growth, 50.0, 300.0)
    asteroid_speed_max = _clamp(100.0 * speed_growth, 100.0, 350.0)
    currency_drop_chance = _clamp(0.4 - (safe_level - 1) * 0.005, 0.2, 1.0)
    currency_value_base = 10 + (safe_level - 1) * 2

    # Enemy parameters (Phase 3 wave spawning)
    if safe_level < 6:
        enemy_spawn_enabled = False
        enemy_count_max = 0
        enemy_spawn_interval = 10.0
        enemy_aggression = 0.0
        aggressive_ratio = 0.0
    else:
        enemy_spawn_enabled = True
        # enemy_count_max: 1 at level 6, 3 at level 10, 5 at level 15, 8 at level 20+
        if safe_level <= 10:
            enemy_count_max = int(round(_clamp(1 + (safe_level - 6) * 0.5, 1.0, 3.0)))
        elif safe_level <= 15:
            enemy_count_max = int(round(_clamp(3 + (safe_level - 10) * 0.4, 3.0, 5.0)))
        else:
            enemy_count_max = int(round(_clamp(5 + (safe_level - 15) * 0.6, 5.0, 8.0)))
        # enemy_spawn_interval: 8.0s at level 6 down to 3.0s at level 20+
        enemy_spawn_interval = _clamp(
            8.0 - (safe_level - 6) * (5.0 / 14.0), 3.0, 8.0
        )
        # aggressive_ratio: 0.0 at level 6, 0.3 at level 10, 0.5 at level 15, 0.7 at level 25+
        if safe_level <= 10:
            aggressive_ratio = _clamp((safe_level - 6) * 0.075, 0.0, 0.3)
        elif safe_level <= 15:
            aggressive_ratio = _clamp(0.3 + (safe_level - 10) * 0.04, 0.3, 0.5)
        elif safe_level <= 25:
            aggressive_ratio = _clamp(0.5 + (safe_level - 15) * 0.02, 0.5, 0.7)
        else:
            aggressive_ratio = 0.7
        # enemy_aggression: 0.3 at level 6 up to 0.9 at level 25+
        enemy_aggression = _clamp(0.3 + (safe_level - 6) * 0.0316, 0.3, 0.9)

    return DifficultyParams(
        asteroid_count=asteroid_count,
        asteroid_speed_min=asteroid_speed_min,
        asteroid_speed_max=asteroid_speed_max,
        enemy_spawn_enabled=enemy_spawn_enabled,
        enemy_count_max=enemy_count_max,
        enemy_spawn_interval=enemy_spawn_interval,
        enemy_aggression=enemy_aggression,
        aggressive_ratio=aggressive_ratio,
        currency_drop_chance=currency_drop_chance,
        currency_value_base=currency_value_base,
    )


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
