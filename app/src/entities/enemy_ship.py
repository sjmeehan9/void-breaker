"""Enemy ship entity with archetype-driven AI and firing behavior."""

from __future__ import annotations

import math
import random

import arcade
from asterax.app.src.config.enemy_config import EnemyArchetype, EnemyConfig
from asterax.app.src.config.game_config import GAME_CONFIG
from asterax.app.src.entities.projectile import Projectile


class EnemyShip(arcade.Sprite):
    """Combat enemy with steering, telegraphed attacks, and health."""

    def __init__(
        self,
        archetype: EnemyArchetype,
        config: EnemyConfig,
        center_x: float,
        center_y: float,
        rng: random.Random | None = None,
    ) -> None:
        """Initialise enemy sprite, movement state, and combat timers.

        Args:
            archetype: Enemy behavior archetype.
            config: Archetype-specific tuning values.
            center_x: Initial horizontal position.
            center_y: Initial vertical position.
            rng: Optional seeded RNG for deterministic tests.
        """
        super().__init__(str(config.sprite_path), center_x=center_x, center_y=center_y)
        self.archetype = archetype
        self.config = config
        self.health = config.health
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.fire_cooldown_remaining = 0.0
        self.spawn_grace_remaining = config.spawn_grace_period
        self.telegraph_remaining = 0.0
        self.is_telegraphing = False
        self._telegraph_elapsed = 0.0
        self._rng = rng if rng is not None else random.Random()
        self._enemy_projectile_texture = arcade.load_texture(
            str(config.projectile_sprite_path)
        )

    @property
    def point_value(self) -> int:
        """Return score value awarded when the enemy is destroyed."""
        return self.config.point_value

    def update_ai(
        self,
        dt: float,
        player_position: tuple[float, float],
    ) -> None:
        """Advance movement and attack timers for this simulation step.

        Args:
            dt: Simulation delta in seconds.
            player_position: Current player world position.
        """
        self._move_toward_player(dt, player_position)
        self.center_x += self.velocity_x * dt
        self.center_y += self.velocity_y * dt

        if self.spawn_grace_remaining > 0.0:
            self.spawn_grace_remaining = max(0.0, self.spawn_grace_remaining - dt)
        if self.fire_cooldown_remaining > 0.0:
            self.fire_cooldown_remaining = max(0.0, self.fire_cooldown_remaining - dt)

        if self.velocity_x != 0.0 or self.velocity_y != 0.0:
            self.angle = (
                math.degrees(math.atan2(self.velocity_y, self.velocity_x)) - 90.0
            )

    def try_fire(
        self,
        dt: float,
        player_position: tuple[float, float],
        player_velocity: tuple[float, float] = (0.0, 0.0),
    ) -> Projectile | None:
        """Begin telegraphing or fire a projectile when all conditions are met.

        Args:
            dt: Simulation delta in seconds.
            player_position: Current player world position.
            player_velocity: Current player velocity for leading shots.

        Returns:
            A projectile when a shot is emitted, otherwise None.
        """
        if self.spawn_grace_remaining > 0.0:
            return None

        if self.is_telegraphing:
            self._update_telegraph(dt)
            if self.is_telegraphing:
                return None
            return self._fire_projectile(player_position, player_velocity)

        if self.fire_cooldown_remaining > 0.0:
            return None

        self.is_telegraphing = True
        self.telegraph_remaining = self.config.telegraph_duration
        self._telegraph_elapsed = 0.0
        self._update_telegraph(0.0)
        return None

    def take_damage(self, amount: float) -> bool:
        """Apply incoming damage and report whether the enemy is destroyed.

        Args:
            amount: Damage value to subtract from health.

        Returns:
            True when health is depleted, otherwise False.
        """
        self.health = max(0.0, self.health - max(0.0, amount))
        return self.health <= 0.0

    def on_destroyed(self) -> dict[str, int | float]:
        """Return configured destruction rewards for manager-level handling."""
        return {
            "point_value": self.config.point_value,
            "currency_drop_chance": self.config.currency_drop_chance,
            "buff_drop_chance": self.config.buff_drop_chance,
        }

    def _move_toward_player(
        self,
        dt: float,
        player_position: tuple[float, float],
    ) -> None:
        """Steer velocity toward the player with slight per-frame jitter."""
        target_x, target_y = player_position
        offset_x = target_x - self.center_x
        offset_y = target_y - self.center_y
        desired_angle = math.degrees(math.atan2(offset_y, offset_x))
        desired_angle += self._rng.uniform(-10.0, 10.0)

        if self.velocity_x == 0.0 and self.velocity_y == 0.0:
            current_angle = self.angle + 90.0
        else:
            current_angle = math.degrees(math.atan2(self.velocity_y, self.velocity_x))

        next_angle = _rotate_toward(
            current_angle=current_angle,
            target_angle=desired_angle,
            max_delta=self.config.turn_rate * dt,
        )
        radians = math.radians(next_angle)
        self.velocity_x = math.cos(radians) * self.config.speed
        self.velocity_y = math.sin(radians) * self.config.speed

    def _calculate_aim(
        self,
        player_position: tuple[float, float],
        player_velocity: tuple[float, float],
    ) -> float:
        """Calculate firing angle with archetype-based prediction and scatter."""
        target_x, target_y = player_position
        if self.archetype is EnemyArchetype.AGGRESSIVE:
            distance = math.hypot(target_x - self.center_x, target_y - self.center_y)
            lead_time = distance / max(1.0, self.config.projectile_speed)
            target_x += player_velocity[0] * lead_time
            target_y += player_velocity[1] * lead_time

        aim_x = target_x - self.center_x
        aim_y = target_y - self.center_y
        base_angle = math.degrees(math.atan2(aim_y, aim_x)) - 90.0
        scatter_limit = (1.0 - max(0.0, min(1.0, self.config.accuracy))) * 20.0
        return base_angle + self._rng.uniform(-scatter_limit, scatter_limit)

    def _update_telegraph(self, dt: float) -> None:
        """Advance telegraph state and apply visual flash while charging."""
        if not self.is_telegraphing:
            return

        self.telegraph_remaining = max(0.0, self.telegraph_remaining - dt)
        self._telegraph_elapsed += dt

        self.alpha = 180 if int(self._telegraph_elapsed * 20.0) % 2 else 255

        if self.telegraph_remaining <= 0.0:
            self.is_telegraphing = False
            self.alpha = 255

    def _fire_projectile(
        self,
        player_position: tuple[float, float],
        player_velocity: tuple[float, float],
    ) -> Projectile:
        """Create a projectile and reset cooldown after telegraph completion."""
        angle = self._calculate_aim(player_position, player_velocity)
        projectile = Projectile(
            center_x=self.center_x,
            center_y=self.center_y,
            angle=angle,
            speed=self.config.projectile_speed,
            max_range=max(GAME_CONFIG.window_width, GAME_CONFIG.window_height),
            damage=self.config.projectile_damage,
        )
        projectile.texture = self._enemy_projectile_texture
        projectile.owner = "enemy"
        self.fire_cooldown_remaining = self.config.fire_cooldown
        return projectile


def _rotate_toward(
    current_angle: float, target_angle: float, max_delta: float
) -> float:
    """Rotate one angle toward another by a bounded delta."""
    delta = (target_angle - current_angle + 180.0) % 360.0 - 180.0
    if abs(delta) <= max_delta:
        return target_angle
    return current_angle + math.copysign(max_delta, delta)
