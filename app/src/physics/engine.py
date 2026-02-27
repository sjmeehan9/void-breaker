"""Physics engine orchestration for fixed-step entity updates."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from asterax.app.src.config.game_config import PhysicsConfig
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.physics.wrap import wrap_entity

if TYPE_CHECKING:
    from asterax.app.src.input.input_manager import InputManager


class HasPlayerShip(Protocol):
    """Protocol for managers that expose a player ship instance."""

    player_ship: PlayerShip


class PhysicsEngine:
    """Applies movement inputs and updates physical state for entities."""

    def __init__(
        self, entity_manager: HasPlayerShip, physics_config: PhysicsConfig
    ) -> None:
        """Construct a physics engine tied to an entity manager.

        Args:
            entity_manager: Object exposing the active player ship.
            physics_config: Physics constants used for simulation.
        """
        self.entity_manager = entity_manager
        self.physics_config = physics_config

    def update(
        self,
        dt: float,
        keys_held: set[int],
        input_manager: InputManager,
        width: float,
        height: float,
    ) -> None:
        """Advance ship physics for one fixed timestep.

        Args:
            dt: Fixed simulation step in seconds.
            keys_held: Active key codes currently held down.
            input_manager: Input manager for action mapping.
            width: Screen width in pixels.
            height: Screen height in pixels.
        """
        del keys_held

        ship = self.entity_manager.player_ship

        rotate_left = input_manager.is_action_held("rotate_left")
        rotate_right = input_manager.is_action_held("rotate_right")
        if rotate_left and not rotate_right:
            ship.apply_rotation(dt, direction=-1)
        elif rotate_right and not rotate_left:
            ship.apply_rotation(dt, direction=1)

        if input_manager.is_action_held("thrust"):
            ship.apply_thrust(dt)

        if input_manager.is_action_held("brake"):
            ship.apply_brake(dt)

        ship.apply_drag(dt)
        ship.cap_speed()
        ship.update_position(dt)
        ship.update_cooldown(dt)
        wrap_entity(ship, width, height)

        if input_manager.is_action_held("fire") and hasattr(
            self.entity_manager, "player_projectiles"
        ):
            ship.fire(getattr(self.entity_manager, "player_projectiles"))

        for asteroid in getattr(self.entity_manager, "asteroids", ()):
            asteroid.update(dt)
            wrap_entity(asteroid, width, height)

        for projectile in list(getattr(self.entity_manager, "player_projectiles", ())):
            projectile.update(dt)
            wrap_entity(projectile, width, height)

        for pickup in list(getattr(self.entity_manager, "currency_pickups", ())):
            pickup.update(dt)
            wrap_entity(pickup, width, height)
