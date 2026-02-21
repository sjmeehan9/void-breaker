"""Pause overlay stub state."""

import arcade
from asterax.app.src.states.base_state import BaseState


class PauseState(BaseState):
    """Overlay pause menu for combat/shop phases."""

    def on_draw(self) -> None:
        """Draw a dimming overlay and pause instructions."""
        window = arcade.get_window()
        arcade.draw_lrbt_rectangle_filled(
            0,
            window.width,
            0,
            window.height,
            (0, 0, 0, 160),
        )
        arcade.draw_text(
            "PAUSED\nESC: Resume  R: Restart  M: Main Menu",
            window.width / 2,
            window.height / 2,
            arcade.color.WHITE,
            28,
            anchor_x="center",
            multiline=True,
            width=760,
            align="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle pause actions."""
        del modifiers

        from asterax.app.src.states.game_init import GameInitState
        from asterax.app.src.states.main_menu import MainMenuState

        if key == arcade.key.ESCAPE:
            self.state_machine.pop_state()
        elif key == arcade.key.R:
            self.state_machine.switch_state(GameInitState(self.state_machine))
        elif key == arcade.key.M:
            self.state_machine.switch_state(MainMenuState(self.state_machine))
