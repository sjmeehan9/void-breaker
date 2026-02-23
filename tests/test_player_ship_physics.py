"""Unit tests for PlayerShip physics and wrap-around utilities."""

from __future__ import annotations

import math
from pathlib import Path

from asterax.app.src.config.game_config import GAME_CONFIG, PhysicsConfig
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.physics.wrap import wrap_entity


class MockEntity:
    """Minimal bounds-based entity used to test wrap logic."""

    def __init__(
        self, center_x: float, center_y: float, width: float, height: float
    ) -> None:
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height

    @property
    def left(self) -> float:
        return self.center_x - self.width / 2

    @left.setter
    def left(self, value: float) -> None:
        self.center_x = value + self.width / 2

    @property
    def right(self) -> float:
        return self.center_x + self.width / 2

    @right.setter
    def right(self, value: float) -> None:
        self.center_x = value - self.width / 2

    @property
    def bottom(self) -> float:
        return self.center_y - self.height / 2

    @bottom.setter
    def bottom(self, value: float) -> None:
        self.center_y = value + self.height / 2

    @property
    def top(self) -> float:
        return self.center_y + self.height / 2

    @top.setter
    def top(self, value: float) -> None:
        self.center_y = value - self.height / 2


def _make_ship() -> PlayerShip:
    sprite_path = (
        Path(__file__).resolve().parents[1] / "assets" / "sprites" / "ship.png"
    )
    return PlayerShip(
        sprite_path=sprite_path,
        center_x=640.0,
        center_y=480.0,
        physics_config=PhysicsConfig(),
    )


def test_apply_thrust_increases_velocity_in_facing_direction() -> None:
    """Thrust should accelerate the ship in its current facing direction."""
    ship = _make_ship()
    ship.angle = 0.0

    ship.apply_thrust(1.0)

    assert abs(ship.velocity_x) < 1e-6
    assert ship.velocity_y > 0.0


def test_apply_drag_reduces_velocity_over_time() -> None:
    """Natural drag should gradually reduce existing velocity."""
    ship = _make_ship()
    ship.velocity_x = 100.0
    ship.velocity_y = 0.0

    ship.apply_drag(1.0)

    assert ship.velocity_x == 70.0
    assert ship.velocity_y == 0.0


def test_brake_reduces_velocity_faster_than_natural_drag() -> None:
    """Brake drag should decelerate more than passive natural drag."""
    ship_drag = _make_ship()
    ship_brake = _make_ship()
    ship_drag.velocity_x = 100.0
    ship_brake.velocity_x = 100.0

    ship_drag.apply_drag(0.1)
    ship_brake.apply_brake(0.1)

    assert ship_brake.velocity_x < ship_drag.velocity_x


def test_cap_speed_limits_velocity_magnitude() -> None:
    """Velocity magnitude should never exceed max_ship_speed after capping."""
    ship = _make_ship()
    ship.velocity_x = 1000.0
    ship.velocity_y = 1000.0

    ship.cap_speed()

    assert (
        math.hypot(ship.velocity_x, ship.velocity_y)
        <= ship.physics_config.max_ship_speed
    )


def test_rotation_changes_angle_at_turn_rate() -> None:
    """Rotation should apply base_turn_rate * dt degrees per update."""
    ship = _make_ship()

    ship.apply_rotation(0.5, direction=1)

    assert ship.angle == 120.0


def test_wrap_entity_handles_all_edges() -> None:
    """wrap_entity should move entities to opposite sides for each out-of-bounds edge."""
    width = 100.0
    height = 80.0

    left_exit = MockEntity(center_x=-20.0, center_y=40.0, width=10.0, height=10.0)
    wrap_entity(left_exit, width, height)
    assert left_exit.left == width

    right_exit = MockEntity(center_x=120.0, center_y=40.0, width=10.0, height=10.0)
    wrap_entity(right_exit, width, height)
    assert right_exit.right == 0.0

    bottom_exit = MockEntity(center_x=50.0, center_y=-20.0, width=10.0, height=10.0)
    wrap_entity(bottom_exit, width, height)
    assert bottom_exit.bottom == height

    top_exit = MockEntity(center_x=50.0, center_y=120.0, width=10.0, height=10.0)
    wrap_entity(top_exit, width, height)
    assert top_exit.top == 0.0


def test_take_damage_reduces_shields_and_reports_death() -> None:
    """Damage should reduce shields and return True when depleted."""
    ship = _make_ship()

    dead = ship.take_damage(150.0)

    assert ship.shields == 0.0
    assert dead is True


def test_take_damage_ignores_hits_while_invulnerable() -> None:
    """Damage should be ignored while invulnerability is active."""
    ship = _make_ship()
    ship.take_damage(5.0)
    shields_after_first_hit = ship.shields

    dead = ship.take_damage(10.0)

    assert dead is False
    assert ship.shields == shields_after_first_hit


def test_update_invulnerability_expires_after_configured_duration() -> None:
    """Invulnerability should clear once its configured duration elapses."""
    ship = _make_ship()
    ship.take_damage(5.0)
    assert ship.is_invulnerable is True

    ship.update_invulnerability(GAME_CONFIG.invulnerability_duration)

    assert ship.is_invulnerable is False
