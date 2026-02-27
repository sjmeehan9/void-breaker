"""Player ship entity with inertial movement and shield tracking."""

from __future__ import annotations

import math
from pathlib import Path

import arcade
from asterax.app.src.config.game_config import GAME_CONFIG, PhysicsConfig
from asterax.app.src.entities.projectile import Projectile


class PlayerShip(arcade.Sprite):
    """Player-controlled ship implementing inertial physics behaviors."""

    def __init__(
        self,
        sprite_path: Path,
        center_x: float,
        center_y: float,
        physics_config: PhysicsConfig,
    ) -> None:
        """Initialize a player ship instance.

        Args:
            sprite_path: Absolute path to the ship sprite texture.
            center_x: Initial horizontal position in pixels.
            center_y: Initial vertical position in pixels.
            physics_config: Physics constants for movement and combat values.
        """
        super().__init__(str(sprite_path), center_x=center_x, center_y=center_y)
        self.physics_config = physics_config
        self.velocity_x: float = 0.0
        self.velocity_y: float = 0.0
        self.shields: float = physics_config.max_shields
        self.max_shields: float = physics_config.max_shields
        self.fire_cooldown_remaining: float = 0.0
        self._invulnerability_timer: float = 0.0
        self._damage_boost_active: bool = False
        self._damage_boost_multiplier: float = 1.0
        self._speed_boost_active: bool = False
        self._speed_boost_multiplier: float = 1.0
        self._damage_flash_remaining: float = 0.0
        self._damage_flash_duration: float = 0.0

    @property
    def effective_damage(self) -> float:
        """Return projectile damage including temporary buff modifiers."""
        return self.physics_config.base_damage * self._damage_boost_multiplier

    @property
    def effective_thrust(self) -> float:
        """Return thrust force including temporary buff modifiers."""
        return self.physics_config.base_thrust * self._speed_boost_multiplier

    @property
    def invulnerability_timer(self) -> float:
        """Return remaining invulnerability time in seconds."""
        return self._invulnerability_timer

    @property
    def is_invulnerable(self) -> bool:
        """Return whether the ship is currently invulnerable."""
        return self._invulnerability_timer > 0.0

    def apply_thrust(self, dt: float) -> None:
        """Apply forward thrust in the ship's facing direction.

        Args:
            dt: Fixed simulation step in seconds.
        """
        angle_radians = math.radians(self.angle + 90.0)
        thrust_x = math.cos(angle_radians) * self.effective_thrust
        thrust_y = math.sin(angle_radians) * self.effective_thrust
        self.velocity_x += thrust_x * dt
        self.velocity_y += thrust_y * dt

    def apply_rotation(self, dt: float, direction: int) -> None:
        """Rotate ship left or right by turn rate.

        Args:
            dt: Fixed simulation step in seconds.
            direction: Rotation direction (-1 for right, +1 for left).
        """
        self.angle += direction * self.physics_config.base_turn_rate * dt

    def apply_brake(self, dt: float) -> None:
        """Apply strong braking drag to current velocity.

        Args:
            dt: Fixed simulation step in seconds.
        """
        brake_factor = max(0.0, 1.0 - self.physics_config.brake_drag * dt)
        self.velocity_x *= brake_factor
        self.velocity_y *= brake_factor

    def apply_drag(self, dt: float) -> None:
        """Apply passive drag for gradual deceleration.

        Args:
            dt: Fixed simulation step in seconds.
        """
        drag_factor = max(0.0, 1.0 - self.physics_config.natural_drag * dt)
        self.velocity_x *= drag_factor
        self.velocity_y *= drag_factor

    def cap_speed(self) -> None:
        """Clamp velocity magnitude to configured maximum ship speed."""
        current_speed = math.hypot(self.velocity_x, self.velocity_y)
        if current_speed <= self.physics_config.max_ship_speed or current_speed == 0.0:
            return

        scale = self.physics_config.max_ship_speed / current_speed
        self.velocity_x *= scale
        self.velocity_y *= scale

    def update_position(self, dt: float) -> None:
        """Advance position using current velocity.

        Args:
            dt: Fixed simulation step in seconds.
        """
        self.center_x += self.velocity_x * dt
        self.center_y += self.velocity_y * dt

    def update_cooldown(self, dt: float) -> None:
        """Advance internal cooldown and invulnerability timers.

        Args:
            dt: Fixed simulation step in seconds.
        """
        self.fire_cooldown_remaining = max(0.0, self.fire_cooldown_remaining - dt)
        self.update_invulnerability(dt)

    def tick_cooldowns(self, dt: float) -> None:
        """Backward-compatible cooldown ticking wrapper."""
        self.update_cooldown(dt)

    def fire(self, projectile_list: arcade.SpriteList) -> Projectile | None:
        """Spawn a projectile when the fire cooldown allows.

        Args:
            projectile_list: Sprite list that owns active player projectiles.

        Returns:
            The created projectile when fired, otherwise None.
        """
        if self.fire_cooldown_remaining > 0.0:
            return None

        angle_radians = math.radians(self.angle + 90.0)
        nose_offset = self.height / 2
        projectile = Projectile(
            center_x=self.center_x + math.cos(angle_radians) * nose_offset,
            center_y=self.center_y + math.sin(angle_radians) * nose_offset,
            angle=self.angle,
            speed=self.physics_config.base_projectile_speed,
            max_range=self.physics_config.base_projectile_range,
            damage=self.effective_damage,
        )
        projectile_list.append(projectile)
        self.fire_cooldown_remaining = 1.0 / self.physics_config.base_fire_rate
        return projectile

    def take_damage(self, amount: float) -> bool:
        """Apply damage to shields and report death state.

        Args:
            amount: Incoming damage amount.

        Returns:
            True when shields are depleted to zero, otherwise False.
        """
        if self.is_invulnerable:
            return False
        self.shields = max(0.0, self.shields - amount)
        self._invulnerability_timer = GAME_CONFIG.invulnerability_duration
        return self.shields <= 0.0

    def update_invulnerability(self, dt: float) -> None:
        """Advance the invulnerability timer by elapsed simulation time."""
        self._invulnerability_timer = max(0.0, self._invulnerability_timer - dt)
        self.update_damage_flash(dt)

    def trigger_damage_flash_tint(self, duration: float = 0.2) -> None:
        """Start or refresh a brief red/white damage flash."""
        self._damage_flash_duration = max(0.01, duration)
        self._damage_flash_remaining = self._damage_flash_duration

    def update_damage_flash(self, dt: float) -> None:
        """Update damage flash tint state and restore default color when complete."""
        if self._damage_flash_remaining <= 0.0:
            return
        self._damage_flash_remaining = max(
            0.0, self._damage_flash_remaining - max(0.0, dt)
        )
        progress = 1.0 - (self._damage_flash_remaining / self._damage_flash_duration)
        phase = int(progress * 8.0)
        self.color = (255, 60, 60) if phase % 2 == 0 else arcade.color.WHITE
        if self._damage_flash_remaining <= 0.0:
            self.color = arcade.color.WHITE

    def apply_damage_boost(self, multiplier: float) -> None:
        """Apply or refresh the temporary projectile-damage multiplier."""
        self._damage_boost_active = True
        self._damage_boost_multiplier = max(1.0, multiplier)

    def remove_damage_boost(self) -> None:
        """Remove any active projectile-damage buff and restore baseline damage."""
        self._damage_boost_active = False
        self._damage_boost_multiplier = 1.0

    def apply_speed_boost(self, multiplier: float) -> None:
        """Apply or refresh the temporary thrust multiplier."""
        self._speed_boost_active = True
        self._speed_boost_multiplier = max(1.0, multiplier)

    def remove_speed_boost(self) -> None:
        """Remove any active thrust buff and restore baseline thrust."""
        self._speed_boost_active = False
        self._speed_boost_multiplier = 1.0
