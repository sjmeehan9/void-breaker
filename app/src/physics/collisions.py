"""Collision detection and response orchestration for combat entities."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import arcade
from asterax.app.src.config.game_config import CURRENCY_CONFIG
from asterax.app.src.entities.pickups import CurrencyPickup

if TYPE_CHECKING:
    from asterax.app.src.audio.audio_manager import AudioManager
    from asterax.app.src.entities.asteroid import Asteroid
    from asterax.app.src.entities.player_ship import PlayerShip
    from asterax.app.src.entities.projectile import Projectile
    from asterax.app.src.managers.currency_manager import CurrencyManager
    from asterax.app.src.managers.score_manager import ScoreManager
    from asterax.app.src.managers.spawn_manager import SpawnManager


class CollisionSystem:
    """Handle all active collision pairs for the combat phase."""

    def __init__(self, collision_damage: float = 25.0) -> None:
        """Initialize configurable collision response values."""
        self.collision_damage = collision_damage
        self._ghost_sprites: list[arcade.Sprite] = []

    def check_all(
        self,
        entity_manager: object,
        game_state: object,
        spawn_manager: SpawnManager,
        score_manager: ScoreManager,
        screen_width: float,
        screen_height: float,
        currency_manager: CurrencyManager | None = None,
        audio_manager: AudioManager | None = None,
    ) -> None:
        """Run collision checks for current frame and dispatch responses."""
        (
            ghost_projectile_map,
            ghost_ship_map,
            ghost_asteroid_map,
            ghost_asteroids,
        ) = self._create_ghost_sprites(entity_manager, screen_width, screen_height)
        try:
            self._check_projectiles_vs_asteroids(
                entity_manager=entity_manager,
                ghost_projectile_map=ghost_projectile_map,
                ghost_asteroid_map=ghost_asteroid_map,
                ghost_asteroids=ghost_asteroids,
                spawn_manager=spawn_manager,
                score_manager=score_manager,
            )
            self._check_ship_vs_asteroids(
                entity_manager=entity_manager,
                ghost_ship_map=ghost_ship_map,
                ghost_asteroid_map=ghost_asteroid_map,
                ghost_asteroids=ghost_asteroids,
            )
            self._check_ship_vs_pickups(
                entity_manager=entity_manager,
                game_state=game_state,
                currency_manager=currency_manager,
                audio_manager=audio_manager,
            )
        finally:
            self._cleanup_ghost_sprites()

    def _check_projectiles_vs_asteroids(
        self,
        entity_manager: object,
        ghost_projectile_map: dict[arcade.Sprite, Projectile],
        ghost_asteroid_map: dict[arcade.Sprite, Asteroid],
        ghost_asteroids: arcade.SpriteList,
        spawn_manager: SpawnManager,
        score_manager: ScoreManager,
    ) -> None:
        processed_asteroids: set[Asteroid] = set()
        projectiles = list(getattr(entity_manager, "player_projectiles", ()))
        for projectile in projectiles:
            self._resolve_projectile_hits(
                projectile=projectile,
                source_projectile=projectile,
                entity_manager=entity_manager,
                ghost_asteroid_map=ghost_asteroid_map,
                ghost_asteroids=ghost_asteroids,
                spawn_manager=spawn_manager,
                score_manager=score_manager,
                processed_asteroids=processed_asteroids,
            )

        for ghost_projectile, original_projectile in ghost_projectile_map.items():
            if original_projectile not in getattr(
                entity_manager, "player_projectiles", ()
            ):
                continue
            self._resolve_projectile_hits(
                projectile=ghost_projectile,
                source_projectile=original_projectile,
                entity_manager=entity_manager,
                ghost_asteroid_map=ghost_asteroid_map,
                ghost_asteroids=ghost_asteroids,
                spawn_manager=spawn_manager,
                score_manager=score_manager,
                processed_asteroids=processed_asteroids,
            )

    def _resolve_projectile_hits(
        self,
        projectile: arcade.Sprite,
        source_projectile: Projectile,
        entity_manager: object,
        ghost_asteroid_map: dict[arcade.Sprite, Asteroid],
        ghost_asteroids: arcade.SpriteList,
        spawn_manager: SpawnManager,
        score_manager: ScoreManager,
        processed_asteroids: set[Asteroid],
    ) -> None:
        if source_projectile not in getattr(entity_manager, "player_projectiles", ()):
            return

        asteroid_hits = list(
            arcade.check_for_collision_with_list(projectile, entity_manager.asteroids)
        )
        for ghost_asteroid in arcade.check_for_collision_with_list(
            projectile, ghost_asteroids
        ):
            asteroid_hits.append(ghost_asteroid_map[ghost_asteroid])

        for asteroid in asteroid_hits:
            if (
                asteroid in processed_asteroids
                or asteroid not in entity_manager.asteroids
            ):
                continue
            processed_asteroids.add(asteroid)
            source_projectile.kill()
            score_manager.award_asteroid_points(asteroid.asteroid_size)
            children = spawn_manager.spawn_child_asteroids(asteroid)
            asteroid.kill()
            for child in children:
                entity_manager.asteroids.append(child)
            self._spawn_currency_pickup(entity_manager, asteroid)
            break

    def _spawn_currency_pickup(
        self, entity_manager: object, asteroid: Asteroid
    ) -> None:
        pickup_list = getattr(entity_manager, "currency_pickups", None)
        if pickup_list is None:
            return
        if random.random() >= asteroid.currency_drop_chance:
            return
        pickup_list.append(
            CurrencyPickup(
                center_x=asteroid.center_x,
                center_y=asteroid.center_y,
                value=CURRENCY_CONFIG.pickup_value,
                lifetime=CURRENCY_CONFIG.pickup_lifetime,
                drift_speed_range=CURRENCY_CONFIG.pickup_drift_speed_range,
            )
        )

    def _check_ship_vs_asteroids(
        self,
        entity_manager: object,
        ghost_ship_map: dict[arcade.Sprite, PlayerShip],
        ghost_asteroid_map: dict[arcade.Sprite, Asteroid],
        ghost_asteroids: arcade.SpriteList,
    ) -> None:
        ship = entity_manager.player_ship
        if self._ship_collides(ship, entity_manager.asteroids):
            ship.take_damage(self.collision_damage)
            return

        if self._ship_collides(ship, ghost_asteroids):
            ship.take_damage(self.collision_damage)
            return

        for ghost_ship in ghost_ship_map:
            if self._ship_collides(ghost_ship, entity_manager.asteroids):
                ship.take_damage(self.collision_damage)
                return
            if self._ship_collides(ghost_ship, ghost_asteroids):
                ship.take_damage(self.collision_damage)
                return

        del ghost_asteroid_map

    def _ship_collides(self, ship: arcade.Sprite, targets: arcade.SpriteList) -> bool:
        return bool(arcade.check_for_collision_with_list(ship, targets))

    def _check_ship_vs_pickups(
        self,
        entity_manager: object,
        game_state: object,
        currency_manager: CurrencyManager | None,
        audio_manager: AudioManager | None,
    ) -> None:
        pickup_list = getattr(entity_manager, "currency_pickups", None)
        ship = getattr(entity_manager, "player_ship", None)
        if pickup_list is None or ship is None:
            return

        for pickup in arcade.check_for_collision_with_list(ship, pickup_list):
            value = int(getattr(pickup, "value", 0))
            if value <= 0:
                pickup.kill()
                continue
            if hasattr(game_state, "currency"):
                game_state.currency += value
            if currency_manager is not None:
                currency_manager.earn(value)
            if audio_manager is not None:
                audio_manager.play("pickup_currency")
            pickup.kill()

    def _create_ghost_sprites(
        self,
        entity_manager: object,
        screen_width: float,
        screen_height: float,
    ) -> tuple[
        dict[arcade.Sprite, Projectile],
        dict[arcade.Sprite, PlayerShip],
        dict[arcade.Sprite, Asteroid],
        arcade.SpriteList,
    ]:
        ghost_projectile_map: dict[arcade.Sprite, Projectile] = {}
        ghost_ship_map: dict[arcade.Sprite, PlayerShip] = {}
        ghost_asteroid_map: dict[arcade.Sprite, Asteroid] = {}
        ghost_asteroids = arcade.SpriteList()

        for projectile in getattr(entity_manager, "player_projectiles", ()):
            for ghost in self._ghosts_for_entity(
                projectile, screen_width, screen_height
            ):
                ghost_projectile_map[ghost] = projectile

        ship = getattr(entity_manager, "player_ship", None)
        if ship is not None:
            for ghost in self._ghosts_for_entity(ship, screen_width, screen_height):
                ghost_ship_map[ghost] = ship

        for asteroid in getattr(entity_manager, "asteroids", ()):
            for ghost in self._ghosts_for_entity(asteroid, screen_width, screen_height):
                ghost_asteroid_map[ghost] = asteroid
                ghost_asteroids.append(ghost)

        return ghost_projectile_map, ghost_ship_map, ghost_asteroid_map, ghost_asteroids

    def _ghosts_for_entity(
        self, entity: arcade.Sprite, screen_width: float, screen_height: float
    ) -> list[arcade.Sprite]:
        x_offsets: list[float] = [0.0]
        y_offsets: list[float] = [0.0]
        if entity.left <= entity.width:
            x_offsets.append(screen_width)
        if entity.right >= screen_width - entity.width:
            x_offsets.append(-screen_width)
        if entity.bottom <= entity.height:
            y_offsets.append(screen_height)
        if entity.top >= screen_height - entity.height:
            y_offsets.append(-screen_height)

        ghosts: list[arcade.Sprite] = []
        for x_offset in x_offsets:
            for y_offset in y_offsets:
                if x_offset == 0.0 and y_offset == 0.0:
                    continue
                ghost = arcade.Sprite(
                    entity.texture,
                    scale=entity.scale,
                    center_x=entity.center_x + x_offset,
                    center_y=entity.center_y + y_offset,
                    angle=entity.angle,
                )
                ghosts.append(ghost)
                self._ghost_sprites.append(ghost)
        return ghosts

    def _cleanup_ghost_sprites(self) -> None:
        for ghost in self._ghost_sprites:
            ghost.remove_from_sprite_lists()
        self._ghost_sprites.clear()
