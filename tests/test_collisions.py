"""Phase 2 collision tests for direct and seam-crossing contacts."""

from __future__ import annotations

import random

from asterax.app.src.config.game_config import AsteroidSize, GameState
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.entities.projectile import Projectile
from asterax.app.src.managers.spawn_manager import SpawnManager


def _spawn_manager() -> SpawnManager:
    return SpawnManager(rng=random.Random(4))


def test_projectile_asteroid_collision(
    entity_manager, collision_system, score_manager
) -> None:
    """Projectile impact should remove asteroid and award score."""
    entity_manager.player_ship.center_x = 1000.0
    entity_manager.player_ship.center_y = 1000.0
    asteroid = Asteroid(
        size=AsteroidSize.SMALL,
        center_x=100.0,
        center_y=100.0,
        velocity=(0.0, 0.0),
        rotation_speed=0.0,
        rng=random.Random(1),
    )
    projectile = Projectile(
        center_x=100.0,
        center_y=100.0,
        angle=0.0,
        speed=0.0,
        max_range=600.0,
        damage=1.0,
    )
    entity_manager.asteroids.append(asteroid)
    entity_manager.player_projectiles.append(projectile)

    collision_system.check_all(
        entity_manager=entity_manager,
        game_state=GameState(),
        spawn_manager=_spawn_manager(),
        score_manager=score_manager,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert asteroid not in entity_manager.asteroids
    assert score_manager.score == 100


def test_projectile_asteroid_miss(
    entity_manager, collision_system, score_manager
) -> None:
    """Separated projectile and asteroid should not register collision."""
    asteroid = Asteroid(
        size=AsteroidSize.SMALL,
        center_x=500.0,
        center_y=500.0,
        velocity=(0.0, 0.0),
        rotation_speed=0.0,
        rng=random.Random(2),
    )
    projectile = Projectile(
        center_x=100.0,
        center_y=100.0,
        angle=0.0,
        speed=0.0,
        max_range=600.0,
        damage=1.0,
    )
    entity_manager.asteroids.append(asteroid)
    entity_manager.player_projectiles.append(projectile)

    collision_system.check_all(
        entity_manager=entity_manager,
        game_state=GameState(),
        spawn_manager=_spawn_manager(),
        score_manager=score_manager,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert asteroid in entity_manager.asteroids
    assert projectile in entity_manager.player_projectiles
    assert score_manager.score == 0


def test_ghost_sprite_edge_collision(
    entity_manager, collision_system, score_manager
) -> None:
    """Ghost sprites should detect collisions across horizontal screen seams."""
    entity_manager.player_ship.center_x = 300.0
    entity_manager.player_ship.center_y = 300.0
    asteroid = Asteroid(
        size=AsteroidSize.SMALL,
        center_x=1275.0,
        center_y=300.0,
        velocity=(0.0, 0.0),
        rotation_speed=0.0,
        rng=random.Random(3),
    )
    projectile = Projectile(
        center_x=5.0,
        center_y=300.0,
        angle=0.0,
        speed=0.0,
        max_range=600.0,
        damage=1.0,
    )
    entity_manager.asteroids.append(asteroid)
    entity_manager.player_projectiles.append(projectile)

    collision_system.check_all(
        entity_manager=entity_manager,
        game_state=GameState(),
        spawn_manager=_spawn_manager(),
        score_manager=score_manager,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert asteroid not in entity_manager.asteroids
    assert projectile not in entity_manager.player_projectiles


def test_ship_asteroid_collision_damage(
    entity_manager, collision_system, score_manager
) -> None:
    """Direct ship contact with an asteroid should reduce shields."""
    ship = entity_manager.player_ship
    asteroid = Asteroid(
        size=AsteroidSize.SMALL,
        center_x=ship.center_x,
        center_y=ship.center_y,
        velocity=(0.0, 0.0),
        rotation_speed=0.0,
        rng=random.Random(5),
    )
    entity_manager.asteroids.append(asteroid)

    collision_system.check_all(
        entity_manager=entity_manager,
        game_state=GameState(),
        spawn_manager=_spawn_manager(),
        score_manager=score_manager,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert ship.shields == ship.max_shields - collision_system.collision_damage
