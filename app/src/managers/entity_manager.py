"""Central owner for active gameplay entity collections."""

from __future__ import annotations

import arcade
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.entities.buff_pickup import BuffPickup
from asterax.app.src.entities.enemy_ship import EnemyShip
from asterax.app.src.entities.pickups import CurrencyPickup
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.entities.projectile import Projectile


class EntityManager:
    """Own all active entity sprite collections and draw them in z-order."""

    def __init__(self) -> None:
        """Initialize empty entity collections."""
        self.player: PlayerShip | None = None
        self.background_renderer: object | None = None
        self.asteroids: arcade.SpriteList[Asteroid] = arcade.SpriteList(
            use_spatial_hash=True
        )
        self.enemies: arcade.SpriteList[EnemyShip] = arcade.SpriteList()
        self.enemy_projectiles: arcade.SpriteList[Projectile] = arcade.SpriteList()
        self.player_projectiles: arcade.SpriteList[Projectile] = arcade.SpriteList()
        self.currency_pickups: arcade.SpriteList[CurrencyPickup] = arcade.SpriteList()
        self.buff_pickups: arcade.SpriteList[BuffPickup] = arcade.SpriteList()
        self.particles: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()

    @property
    def player_ship(self) -> PlayerShip | None:
        """Backward-compatible alias for player ship access."""
        return self.player

    @player_ship.setter
    def player_ship(self, player: PlayerShip | None) -> None:
        """Backward-compatible alias for assigning active player ship."""
        self.player = player

    def add_asteroid(self, asteroid: Asteroid) -> None:
        """Add an asteroid to the managed asteroid collection."""
        self.asteroids.append(asteroid)

    def remove_asteroid(self, asteroid: Asteroid) -> None:
        """Remove an asteroid from the managed asteroid collection."""
        if asteroid in self.asteroids:
            asteroid.remove_from_sprite_lists()

    def add_projectile(self, projectile: Projectile) -> None:
        """Add a player projectile to the managed projectile collection."""
        self.player_projectiles.append(projectile)

    def remove_projectile(self, projectile: Projectile) -> None:
        """Remove a player projectile from the managed projectile collection."""
        if projectile in self.player_projectiles:
            projectile.remove_from_sprite_lists()

    def add_currency_pickup(self, pickup: CurrencyPickup) -> None:
        """Add a currency pickup to the managed pickup collection."""
        self.currency_pickups.append(pickup)

    def remove_currency_pickup(self, pickup: CurrencyPickup) -> None:
        """Remove a currency pickup from the managed pickup collection."""
        if pickup in self.currency_pickups:
            pickup.remove_from_sprite_lists()

    def add_particle(self, particle: arcade.Sprite) -> None:
        """Add a particle sprite to the managed particle collection."""
        self.particles.append(particle)

    def draw(self) -> None:
        """Draw entities in stable z-order for gameplay readability."""
        if self.background_renderer is not None and hasattr(
            self.background_renderer, "draw"
        ):
            self.background_renderer.draw()
        self.asteroids.draw()
        self.currency_pickups.draw()
        self.buff_pickups.draw()
        self.particles.draw()
        self.enemies.draw()
        self.enemy_projectiles.draw()
        self.player_projectiles.draw()
        if self.player is not None:
            self.player.draw()

    def clear_projectiles(self) -> None:
        """Clear active player projectiles."""
        self.player_projectiles.clear()

    def clear_all(self) -> None:
        """Clear all managed entities for level transitions or teardown."""
        self.asteroids.clear()
        self.clear_enemies()
        self.player_projectiles.clear()
        self.currency_pickups.clear()
        self.buff_pickups.clear()
        self.particles.clear()
        self.player = None

    def clear_enemies(self) -> None:
        """Clear active enemies and enemy projectiles."""
        self.enemies.clear()
        self.enemy_projectiles.clear()
