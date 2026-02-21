"""Combat phase stub state."""

import arcade
from asterax.app.src.states.base_state import BaseState


class CombatPhaseState(BaseState):
    """Placeholder combat phase with transition shortcuts."""

    def on_draw(self) -> None:
        """Render combat placeholder text."""
        window = arcade.get_window()
        arcade.draw_text(
            "Combat Phase (stub)\nESC: Pause  N: Shop  G: Game Over",
            window.width / 2,
            window.height / 2,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            multiline=True,
            width=700,
            align="center",
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
