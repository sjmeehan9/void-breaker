"""Phase 2 physics tests for ship movement and wrap behavior."""

from __future__ import annotations

import math

from asterax.app.src.physics.wrap import wrap_entity


class _MockEntity:
    """Minimal object with sprite-like bounds for wrap testing."""

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


def test_thrust_increases_velocity(player_ship) -> None:
    """Thrust should accelerate the ship along its forward axis."""
    player_ship.angle = 0.0
    player_ship.apply_thrust(0.25)
    assert player_ship.velocity_y > 0.0


def test_natural_drag_reduces_velocity(player_ship) -> None:
    """Natural drag should decrease velocity magnitude over time."""
    player_ship.velocity_x = 100.0
    initial_speed = math.hypot(player_ship.velocity_x, player_ship.velocity_y)
    player_ship.apply_drag(1.0)
    assert math.hypot(player_ship.velocity_x, player_ship.velocity_y) < initial_speed


def test_brake_drag_stronger_than_natural(player_ship) -> None:
    """Brake drag should decelerate more aggressively than passive drag."""
    player_ship.velocity_x = 100.0
    player_ship.apply_drag(0.1)
    drag_velocity_x = player_ship.velocity_x
    player_ship.velocity_x = 100.0
    player_ship.apply_brake(0.1)
    assert player_ship.velocity_x < drag_velocity_x


def test_speed_cap_enforced(player_ship) -> None:
    """Speed capping should bound velocity at configured max speed."""
    player_ship.velocity_x = 10000.0
    player_ship.velocity_y = 10000.0
    player_ship.cap_speed()
    assert (
        math.hypot(player_ship.velocity_x, player_ship.velocity_y)
        <= player_ship.physics_config.max_ship_speed
    )


def test_wrap_entity_all_edges() -> None:
    """Entities exiting any edge should wrap to the opposite side."""
    width = 1280.0
    height = 960.0

    left = _MockEntity(-10.0, 300.0, 10.0, 10.0)
    right = _MockEntity(width + 10.0, 300.0, 10.0, 10.0)
    bottom = _MockEntity(300.0, -10.0, 10.0, 10.0)
    top = _MockEntity(300.0, height + 10.0, 10.0, 10.0)

    wrap_entity(left, width, height)
    wrap_entity(right, width, height)
    wrap_entity(bottom, width, height)
    wrap_entity(top, width, height)

    assert left.left == width
    assert right.right == 0.0
    assert bottom.bottom == height
    assert top.top == 0.0


def test_wrap_entity_corner() -> None:
    """Entities exiting two edges should wrap on both axes."""
    entity = _MockEntity(-10.0, -10.0, 10.0, 10.0)
    wrap_entity(entity, 1280.0, 960.0)
    assert entity.left == 1280.0
    assert entity.bottom == 960.0
