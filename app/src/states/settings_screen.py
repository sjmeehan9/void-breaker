"""Settings stub state."""

import arcade
from asterax.app.src.states.base_state import BaseState


class SettingsScreenState(BaseState):
    """Placeholder settings screen."""

    def on_draw(self) -> None:
        """Render settings placeholder text."""
        window = arcade.get_window()
        arcade.draw_text(
            "Settings (stub)\nESC/Backspace: Main Menu",
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
        """Return to main menu."""
        del modifiers

        from asterax.app.src.states.main_menu import MainMenuState

        if key in (arcade.key.ESCAPE, arcade.key.BACKSPACE):
            self.state_machine.switch_state(MainMenuState(self.state_machine))
