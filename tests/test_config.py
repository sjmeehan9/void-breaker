"""Tests for game configuration, upgrade definitions, and data models."""

from asterax.app.src.config.difficulty_tables import get_difficulty
from asterax.app.src.config.game_config import (
    CURRENCY_CONFIG,
    GAME_CONFIG,
    AsteroidSize,
    DifficultyParams,
    EnemyArchetype,
    GamePhase,
    GameState,
    InsuranceState,
    InsuranceTier,
    LevelStats,
    RunStats,
    ShipState,
    UpgradeCategory,
)
from asterax.app.src.config.upgrade_definitions import (
    UPGRADE_DEFINITIONS,
    get_upgrade_by_id,
    get_upgrade_cost,
)


def test_game_config_defaults_match_component_spec() -> None:
    """GAME_CONFIG should expose required fixed constants."""
    assert GAME_CONFIG.physics_dt == 1.0 / 60.0
    assert GAME_CONFIG.max_frame_time == 0.25
    assert GAME_CONFIG.target_fps == 60
    assert GAME_CONFIG.window_width == 1280
    assert GAME_CONFIG.window_height == 960
    assert GAME_CONFIG.window_title == "VoidBreaker"
    assert GAME_CONFIG.max_ship_speed == 600.0
    assert GAME_CONFIG.base_shields == 100.0
    assert GAME_CONFIG.max_high_scores == 100
    assert GAME_CONFIG.max_player_projectiles == 15
    assert CURRENCY_CONFIG.pickup_value == 10
    assert CURRENCY_CONFIG.pickup_lifetime == 10.0


def test_upgrade_definitions_are_valid() -> None:
    """Upgrade definitions should contain valid non-empty and positive values."""
    for definition in UPGRADE_DEFINITIONS:
        assert definition.id
        assert definition.name
        assert definition.description
        assert definition.max_level > 0
        assert definition.base_cost > 0
        assert definition.cost_scaling > 0
        assert isinstance(definition.category, UpgradeCategory)


def test_get_upgrade_cost_scales_per_level() -> None:
    """Upgrade costs should follow geometric scaling per current level."""
    definition = get_upgrade_by_id("weapon_fire_rate")
    assert definition is not None

    assert get_upgrade_cost(definition, 0) == 50
    assert get_upgrade_cost(definition, 1) == 75
    assert get_upgrade_cost(definition, 5) == int(50 * (1.5**5))


def test_get_difficulty_scales_and_enables_enemies_progressively() -> None:
    """Difficulty generation should scale asteroid and enemy pressure over levels."""
    samples = [get_difficulty(level) for level in (1, 5, 10, 20, 50)]

    assert samples[0].asteroid_count <= samples[-1].asteroid_count
    # Phase 3: Enemy spawning enabled from level 6+
    assert samples[0].enemy_spawn_enabled is False  # Level 1
    assert samples[1].enemy_spawn_enabled is False  # Level 5
    assert samples[2].enemy_spawn_enabled is True  # Level 10
    assert samples[2].enemy_count_max > 0
    assert samples[-1].enemy_count_max >= samples[2].enemy_count_max


def test_get_difficulty_clamps_extreme_levels() -> None:
    """Difficulty values should remain bounded at extreme levels."""
    params = get_difficulty(150)

    assert params.asteroid_count <= 30
    assert params.asteroid_speed_min <= 300.0
    assert params.asteroid_speed_max <= 400.0
    assert params.enemy_spawn_interval >= 2.5
    assert 0.0 <= params.enemy_aggression <= 1.0
    assert 0.05 <= params.currency_drop_chance <= 1.0


def test_difficulty_modes_relative_to_classic() -> None:
    """Casual should be easier than classic; hard should be harder."""
    classic = get_difficulty(12, "classic")
    casual = get_difficulty(12, "casual")
    hard = get_difficulty(12, "hard")

    assert casual.asteroid_count < classic.asteroid_count
    assert casual.currency_drop_chance > classic.currency_drop_chance
    assert hard.asteroid_count > classic.asteroid_count
    assert hard.currency_drop_chance < classic.currency_drop_chance


def test_models_instantiate_with_defaults() -> None:
    """All required run-model dataclasses should instantiate without args."""
    assert isinstance(GameState(), GameState)
    assert isinstance(ShipState(), ShipState)
    assert isinstance(InsuranceState(), InsuranceState)
    assert isinstance(DifficultyParams(), DifficultyParams)
    assert isinstance(LevelStats(), LevelStats)
    assert isinstance(RunStats(), RunStats)


def test_ship_state_recalculate_effective_stats_applies_upgrades() -> None:
    """Ship effective stats should recompute from base stats and levels."""
    ship = ShipState(
        weapon_fire_rate_level=2,
        weapon_damage_level=1,
        mobility_thrust_level=3,
        defense_shields_level=2,
        economy_magnet_level=1,
    )

    ship.recalculate_effective_stats(UPGRADE_DEFINITIONS)

    assert ship.effective_fire_rate == ship.base_fire_rate + (2 * 0.5)
    assert ship.effective_damage == ship.base_damage + (1 * 0.3)
    assert ship.effective_thrust == ship.base_thrust + (3 * 60.0)
    assert ship.effective_max_shields == ship.base_shields + (2 * 25.0)
    assert ship.effective_magnet_radius == ship.base_magnet_radius + (1 * 50.0)


def test_enums_expose_expected_members() -> None:
    """Core enums should include all required members."""
    assert {phase.name for phase in GamePhase} == {"COMBAT", "SHOP", "GAME_OVER"}
    assert {size.name for size in AsteroidSize} == {"LARGE", "MEDIUM", "SMALL"}
    assert {enemy.name for enemy in EnemyArchetype} == {"BASIC", "AGGRESSIVE", "SNIPER"}
    assert {category.name for category in UpgradeCategory} == {
        "WEAPON",
        "DEFENSE",
        "MOBILITY",
        "ECONOMY",
        "REPAIR",
    }
    assert {tier.name for tier in InsuranceTier} == {"OFF", "BASIC", "PREMIUM"}
