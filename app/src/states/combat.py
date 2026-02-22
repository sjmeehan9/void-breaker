"""Combat phase state with player ship physics integration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import arcade
from asterax.app.src.config.game_config import PHYSICS_CONFIG
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.physics.engine import PhysicsEngine
from asterax.app.src.states.base_state import BaseState

if TYPE_CHECKING:
    from asterax.app.src.states.state_machine import StateMachine
    from asterax.app.src.window import VoidBreakerWindow


class CombatPhaseState(BaseState):
    """Combat phase with controllable player ship and inertial motion."""

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialize combat state data structures."""
        super().__init__(state_machine)
        self.player_ship: PlayerShip | None = None
        self.physics_engine: PhysicsEngine | None = None

    def on_enter(self) -> None:
        """Spawn and initialize player ship at the screen center."""
        window = cast(VoidBreakerWindow, arcade.get_window())
        ship_sprite_path = (
            Path(__file__).resolve().parents[3] / "assets" / "sprites" / "ship.png"
        )
        self.player_ship = PlayerShip(
            sprite_path=ship_sprite_path,
            center_x=window.width / 2,
            center_y=window.height / 2,
            physics_config=PHYSICS_CONFIG,
        )
        self.physics_engine = PhysicsEngine(self, PHYSICS_CONFIG)

    def on_update(self, delta_time: float) -> None:
        """Advance ship simulation with current held-input state."""
        if self.player_ship is None or self.physics_engine is None:
            return

        window = cast(VoidBreakerWindow, arcade.get_window())
        self.physics_engine.update(
            dt=delta_time,
            keys_held=window.input_manager.keys_held,
            input_manager=window.input_manager,
            width=window.width,
            height=window.height,
        )

    def on_draw(self) -> None:
        """Draw combat debug HUD and the player ship sprite."""
        window = arcade.get_window()
        if self.player_ship is not None:
            self.player_ship.draw()

        arcade.draw_text(
            "Combat Phase\nArrow Keys: Rotate/Thrust/Brake\nESC: Pause  N: Shop  G: Game Over",
            24,
            window.height - 24,
            arcade.color.WHITE,
            16,
            anchor_x="left",
            anchor_y="top",
            multiline=True,
            width=560,
            align="left",
        )

        if self.player_ship is not None:
            arcade.draw_text(
                f"Shields: {self.player_ship.shields:.0f}  Speed: "
                f"{(self.player_ship.velocity_x**2 + self.player_ship.velocity_y**2) ** 0.5:.1f}",
                24,
                window.height - 92,
                arcade.color.AQUA,
                14,
                anchor_x="left",
                anchor_y="top",
            )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle combat state transitions."""
        del modifiers

        from asterax.app.src.states.game_over import GameOverState
        from asterax.app.src.states.pause import PauseState
        from asterax.app.src.states.shop import ShopPhaseState

        if key == arcade.key.ESCAPE:
            self.state_machine.push_state(PauseState(self.state_machine))
        elif key == arcade.key.N:
            self.state_machine.switch_state(ShopPhaseState(self.state_machine))
        elif key == arcade.key.G:
            self.state_machine.switch_state(GameOverState(self.state_machine))
