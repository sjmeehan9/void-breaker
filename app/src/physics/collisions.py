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
    from asterax.app.src.entities.buff_pickup import BuffPickup
    from asterax.app.src.entities.enemy_ship import EnemyShip
    from asterax.app.src.entities.player_ship import PlayerShip
    from asterax.app.src.entities.projectile import Projectile
    from asterax.app.src.managers.currency_manager import CurrencyManager
    from asterax.app.src.managers.score_manager import ScoreManager
    from asterax.app.src.managers.spawn_manager import SpawnManager
    from asterax.app.src.rendering.particle_system import ParticleSystem


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
        particle_system: ParticleSystem | None = None,
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
                particle_system=particle_system,
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

    def check_player_vs_enemy_projectiles(
        self,
        entity_manager: object,
        screen_width: float,
        screen_height: float,
    ) -> list[tuple[PlayerShip, Projectile]]:
        """Return all player-vs-enemy-projectile contacts, including seam ghosts."""
        ship = getattr(entity_manager, "player_ship", None)
        enemy_projectiles = getattr(entity_manager, "enemy_projectiles", None)
        if ship is None or enemy_projectiles is None:
            return []

        try:
            hits = self._check_collisions_with_ghosts(
                source=ship,
                targets=enemy_projectiles,
                screen_width=screen_width,
                screen_height=screen_height,
            )
            return [(ship, projectile) for projectile in hits]
        finally:
            self._cleanup_ghost_sprites()

    def check_player_projectiles_vs_enemies(
        self,
        entity_manager: object,
        screen_width: float,
        screen_height: float,
    ) -> list[tuple[Projectile, EnemyShip]]:
        """Return all player-projectile-vs-enemy contacts, including seam ghosts."""
        player_projectiles = getattr(entity_manager, "player_projectiles", None)
        enemies = getattr(entity_manager, "enemies", None)
        if player_projectiles is None or enemies is None:
            return []

        collisions: list[tuple[Projectile, EnemyShip]] = []
        seen_pairs: set[tuple[int, int]] = set()
        try:
            for projectile in list(player_projectiles):
                if projectile not in player_projectiles:
                    continue
                for enemy in self._check_collisions_with_ghosts(
                    source=projectile,
                    targets=enemies,
                    screen_width=screen_width,
                    screen_height=screen_height,
                ):
                    pair_key = (id(projectile), id(enemy))
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)
                    collisions.append((projectile, enemy))
            return collisions
        finally:
            self._cleanup_ghost_sprites()

    def check_player_vs_enemies(
        self,
        entity_manager: object,
        screen_width: float,
        screen_height: float,
    ) -> list[tuple[PlayerShip, EnemyShip]]:
        """Return all player-vs-enemy contacts, including seam ghosts."""
        ship = getattr(entity_manager, "player_ship", None)
        enemies = getattr(entity_manager, "enemies", None)
        if ship is None or enemies is None:
            return []

        try:
            hits = self._check_collisions_with_ghosts(
                source=ship,
                targets=enemies,
                screen_width=screen_width,
                screen_height=screen_height,
            )
            return [(ship, enemy) for enemy in hits]
        finally:
            self._cleanup_ghost_sprites()

    def check_player_vs_buff_pickups(
        self,
        entity_manager: object,
        screen_width: float,
        screen_height: float,
    ) -> list[tuple[PlayerShip, BuffPickup]]:
        """Return all player-vs-buff-pickup contacts, including seam ghosts."""
        ship = getattr(entity_manager, "player_ship", None)
        buff_pickups = getattr(entity_manager, "buff_pickups", None)
        if ship is None or buff_pickups is None:
            return []

        try:
            hits = self._check_collisions_with_ghosts(
                source=ship,
                targets=buff_pickups,
                screen_width=screen_width,
                screen_height=screen_height,
            )
            return [(ship, buff_pickup) for buff_pickup in hits]
        finally:
            self._cleanup_ghost_sprites()

    def check_all_combat(
        self,
        entity_manager: object,
        screen_width: float,
        screen_height: float,
    ) -> dict[str, list[tuple[arcade.Sprite, arcade.Sprite]]]:
        """Return enemy-combat collision pairs in a single structured payload."""
        return {
            "player_vs_enemy_projectiles": list(
                self.check_player_vs_enemy_projectiles(
                    entity_manager=entity_manager,
                    screen_width=screen_width,
                    screen_height=screen_height,
                )
            ),
            "player_projectiles_vs_enemies": list(
                self.check_player_projectiles_vs_enemies(
                    entity_manager=entity_manager,
                    screen_width=screen_width,
                    screen_height=screen_height,
                )
            ),
            "player_vs_enemies": list(
                self.check_player_vs_enemies(
                    entity_manager=entity_manager,
                    screen_width=screen_width,
                    screen_height=screen_height,
                )
            ),
            "player_vs_buff_pickups": list(
                self.check_player_vs_buff_pickups(
                    entity_manager=entity_manager,
                    screen_width=screen_width,
                    screen_height=screen_height,
                )
            ),
        }

    def _check_projectiles_vs_asteroids(
        self,
        entity_manager: object,
        ghost_projectile_map: dict[arcade.Sprite, Projectile],
        ghost_asteroid_map: dict[arcade.Sprite, Asteroid],
        ghost_asteroids: arcade.SpriteList,
        spawn_manager: SpawnManager,
        score_manager: ScoreManager,
        particle_system: ParticleSystem | None,
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
                particle_system=particle_system,
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
                particle_system=particle_system,
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
        particle_system: ParticleSystem | None,
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
            if particle_system is not None:
                particle_system.spawn_explosion(
                    (asteroid.center_x, asteroid.center_y), asteroid.asteroid_size
                )
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
            if currency_manager is not None:
                currency_manager.earn(value)
            elif hasattr(game_state, "currency"):
                # Fallback for callers that pass no manager (legacy / isolated tests).
                game_state.currency += value
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

    def _check_collisions_with_ghosts(
        self,
        source: arcade.Sprite,
        targets: arcade.SpriteList,
        screen_width: float,
        screen_height: float,
    ) -> list[arcade.Sprite]:
        """Return unique source-target collisions while accounting for screen seams."""
        hits: dict[int, arcade.Sprite] = {
            id(target): target
            for target in arcade.check_for_collision_with_list(source, targets)
        }

        ghost_target_map: dict[arcade.Sprite, arcade.Sprite] = {}
        ghost_targets = arcade.SpriteList()
        for target in targets:
            for ghost in self._ghosts_for_entity(target, screen_width, screen_height):
                ghost_target_map[ghost] = target
                ghost_targets.append(ghost)

        for ghost_hit in arcade.check_for_collision_with_list(source, ghost_targets):
            original_target = ghost_target_map[ghost_hit]
            hits[id(original_target)] = original_target

        for ghost_source in self._ghosts_for_entity(
            source, screen_width, screen_height
        ):
            for hit in arcade.check_for_collision_with_list(ghost_source, targets):
                hits[id(hit)] = hit
            for ghost_hit in arcade.check_for_collision_with_list(
                ghost_source, ghost_targets
            ):
                original_target = ghost_target_map[ghost_hit]
                hits[id(original_target)] = original_target

        return list(hits.values())

    def _cleanup_ghost_sprites(self) -> None:
        for ghost in self._ghost_sprites:
            ghost.remove_from_sprite_lists()
        self._ghost_sprites.clear()
