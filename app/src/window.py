"""Arcade window implementation for VoidBreaker."""

from typing import Final

import arcade

PHYSICS_DT: Final[float] = 1.0 / 60.0
MAX_FRAME_TIME: Final[float] = 0.25


class VoidBreakerWindow(arcade.Window):
    """Main Arcade window with a fixed-timestep update loop."""

    def __init__(
        self,
        width: int = 1280,
        height: int = 960,
        title: str = "VoidBreaker",
    ) -> None:
        """Initialize the game window and fixed-step timing state."""
        super().__init__(width=width, height=height, title=title, resizable=False)
        self.accumulator: float = 0.0
        self.set_update_rate(PHYSICS_DT)

    def on_update(self, delta_time: float) -> None:
        """Advance simulation using a fixed timestep accumulator."""
        frame_time = min(delta_time, MAX_FRAME_TIME)
        self.accumulator += frame_time

        while self.accumulator >= PHYSICS_DT:
            self._physics_step(PHYSICS_DT)
            self.accumulator -= PHYSICS_DT

    def _physics_step(self, dt: float) -> None:
        """Advance one fixed-duration physics tick."""

    def on_draw(self) -> None:
        """Render a cleared black frame."""
        self.clear()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle key press events."""

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Handle key release events."""
