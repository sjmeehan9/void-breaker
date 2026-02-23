"""Unit tests for enemy configuration and AI entity behaviour."""

from __future__ import annotations

import random
from dataclasses import replace

from asterax.app.src.config.enemy_config import (
    EnemyArchetype,
    get_aggressive_config,
    get_basic_config,
)
from asterax.app.src.entities.enemy_ship import EnemyShip


def test_enemy_config_factories_return_expected_defaults() -> None:
    """Factory helpers should produce expected Phase 3 baseline values."""
    basic = get_basic_config()
    aggressive = get_aggressive_config()

    assert basic.speed == 60.0
    assert basic.point_value == 200
    assert basic.fire_cooldown == 2.5
    assert aggressive.speed == 120.0
    assert aggressive.health == 2.0
    assert aggressive.fire_cooldown == 1.25


def test_enemy_ship_instantiates_for_both_archetypes() -> None:
    """Enemy ship should initialize health and archetype-specific rewards."""
    basic_enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=get_basic_config(),
        center_x=100.0,
        center_y=100.0,
    )
    aggressive_enemy = EnemyShip(
        archetype=EnemyArchetype.AGGRESSIVE,
        config=get_aggressive_config(),
        center_x=200.0,
        center_y=200.0,
    )

    assert basic_enemy.archetype is EnemyArchetype.BASIC
    assert basic_enemy.health == 1.0
    assert aggressive_enemy.archetype is EnemyArchetype.AGGRESSIVE
    assert aggressive_enemy.health == 2.0
    assert aggressive_enemy.point_value == 500


def test_update_ai_moves_enemy_toward_player() -> None:
    """Enemy AI update should reduce distance to the player over time."""
    enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=get_basic_config(),
        center_x=0.0,
        center_y=0.0,
        rng=random.Random(0),
    )
    player_position = (200.0, 0.0)
    before_distance = 200.0

    enemy.update_ai(dt=1.0, player_position=player_position)
    after_distance = ((enemy.center_x - 200.0) ** 2 + enemy.center_y**2) ** 0.5

    assert after_distance < before_distance


def test_try_fire_respects_spawn_grace_period() -> None:
    """Enemy should not begin telegraphing until grace period expires."""
    enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=get_basic_config(),
        center_x=10.0,
        center_y=10.0,
        rng=random.Random(1),
    )
    player_position = (50.0, 50.0)

    enemy.update_ai(dt=0.5, player_position=player_position)
    assert enemy.try_fire(dt=0.2, player_position=player_position) is None
    assert enemy.is_telegraphing is False

    enemy.update_ai(dt=0.6, player_position=player_position)
    assert enemy.try_fire(dt=0.1, player_position=player_position) is None
    assert enemy.is_telegraphing is True


def test_try_fire_respects_cooldown_timing() -> None:
    """Enemy should fire only after telegraph completion and cooldown reset."""
    config = replace(
        get_basic_config(),
        spawn_grace_period=0.0,
        telegraph_duration=0.2,
        accuracy=1.0,
    )
    enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=config,
        center_x=0.0,
        center_y=0.0,
        rng=random.Random(2),
    )
    player_position = (0.0, 100.0)

    assert enemy.try_fire(dt=0.0, player_position=player_position) is None
    assert enemy.is_telegraphing is True

    assert enemy.try_fire(dt=0.1, player_position=player_position) is None
    projectile = enemy.try_fire(dt=0.1, player_position=player_position)
    assert projectile is not None
    assert enemy.fire_cooldown_remaining == config.fire_cooldown

    assert enemy.try_fire(dt=0.5, player_position=player_position) is None
    enemy.update_ai(dt=config.fire_cooldown, player_position=player_position)
    assert enemy.try_fire(dt=0.0, player_position=player_position) is None
    assert enemy.is_telegraphing is True


def test_take_damage_updates_destroyed_status() -> None:
    """Damage application should report alive/dead state accurately."""
    enemy = EnemyShip(
        archetype=EnemyArchetype.AGGRESSIVE,
        config=get_aggressive_config(),
        center_x=0.0,
        center_y=0.0,
    )

    assert enemy.take_damage(1.0) is False
    assert enemy.health == 1.0
    assert enemy.take_damage(1.0) is True
    assert enemy.health == 0.0


def test_basic_targeting_aims_at_current_position() -> None:
    """Basic enemy aiming should target current position without leading."""
    config = replace(get_basic_config(), spawn_grace_period=0.0, accuracy=1.0)
    enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=config,
        center_x=0.0,
        center_y=0.0,
        rng=random.Random(3),
    )

    angle = enemy._calculate_aim(
        player_position=(0.0, 100.0), player_velocity=(200.0, 0.0)
    )
    assert angle == 0.0


def test_aggressive_targeting_leads_player_velocity() -> None:
    """Aggressive enemy aiming should lead moving targets."""
    config = replace(
        get_aggressive_config(),
        spawn_grace_period=0.0,
        accuracy=1.0,
        projectile_speed=100.0,
    )
    enemy = EnemyShip(
        archetype=EnemyArchetype.AGGRESSIVE,
        config=config,
        center_x=0.0,
        center_y=0.0,
        rng=random.Random(4),
    )

    angle = enemy._calculate_aim(
        player_position=(0.0, 100.0), player_velocity=(100.0, 0.0)
    )
    assert angle < 0.0


def test_telegraph_state_transitions_to_fire_and_resets() -> None:
    """Telegraph should transition idle -> telegraphing -> firing -> cooldown."""
    config = replace(
        get_basic_config(),
        spawn_grace_period=0.0,
        telegraph_duration=0.3,
        accuracy=1.0,
    )
    enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=config,
        center_x=0.0,
        center_y=0.0,
    )
    player_position = (0.0, 100.0)

    assert enemy.is_telegraphing is False
    assert enemy.try_fire(dt=0.0, player_position=player_position) is None
    assert enemy.is_telegraphing is True

    assert enemy.try_fire(dt=0.15, player_position=player_position) is None
    assert enemy.is_telegraphing is True
    assert enemy.alpha in {180, 255}

    projectile = enemy.try_fire(dt=0.15, player_position=player_position)
    assert projectile is not None
    assert enemy.is_telegraphing is False
    assert enemy.alpha == 255
