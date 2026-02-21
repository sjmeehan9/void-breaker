"""Main menu state."""

import arcade
from asterax.app.src.states.base_state import BaseState


class MainMenuState(BaseState):
    """Stub main menu with keyboard-driven transitions."""

    def on_draw(self) -> None:
        """Draw menu title and control legend."""
        window = arcade.get_window()
        center_x = window.width / 2
        center_y = window.height / 2

        arcade.draw_text(
            "VoidBreaker - Main Menu",
            center_x,
            center_y + 120,
            arcade.color.WHITE,
            40,
            anchor_x="center",
        )
        arcade.draw_text(
            "1/Enter: New Game\n2: How To Play\n3: High Scores\n4: Settings\nQ: Quit",
            center_x,
            center_y,
            arcade.color.WHITE,
            22,
            anchor_x="center",
            multiline=True,
            width=600,
            align="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Route main menu options to other states."""
        del modifiers

        from asterax.app.src.states.game_init import GameInitState
        from asterax.app.src.states.high_scores import HighScoresState
        from asterax.app.src.states.how_to_play import HowToPlayState
        from asterax.app.src.states.settings_screen import SettingsScreenState

        if key in (arcade.key.KEY_1, arcade.key.ENTER):
            self.state_machine.switch_state(GameInitState(self.state_machine))
        elif key == arcade.key.KEY_2:
            self.state_machine.switch_state(HowToPlayState(self.state_machine))
        elif key == arcade.key.KEY_3:
            self.state_machine.switch_state(HighScoresState(self.state_machine))
        elif key == arcade.key.KEY_4:
            self.state_machine.switch_state(SettingsScreenState(self.state_machine))
        elif key == arcade.key.Q:
            arcade.close_window()
