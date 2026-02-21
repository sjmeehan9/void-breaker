"""Game over stub state."""

import arcade
from asterax.app.src.states.base_state import BaseState


class GameOverState(BaseState):
    """Placeholder game over screen."""

    def on_draw(self) -> None:
        """Render game over placeholder text."""
        window = arcade.get_window()
        arcade.draw_text(
            "Game Over (stub)\nEnter/Escape: Main Menu",
            window.width / 2,
            window.height / 2,
            arcade.color.WHITE,
            30,
            anchor_x="center",
            multiline=True,
            width=700,
            align="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Return to main menu from game over."""
        del modifiers

        from asterax.app.src.states.main_menu import MainMenuState

        if key in (arcade.key.ENTER, arcade.key.ESCAPE):
            self.state_machine.switch_state(MainMenuState(self.state_machine))
