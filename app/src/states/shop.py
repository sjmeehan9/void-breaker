"""Shop phase stub state."""

import arcade
from asterax.app.src.states.base_state import BaseState


class ShopPhaseState(BaseState):
    """Placeholder shop phase with transition shortcuts."""

    def on_draw(self) -> None:
        """Render shop placeholder text."""
        window = arcade.get_window()
        arcade.draw_text(
            "Shop Phase (stub)\nESC: Pause  Enter: Next Combat",
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
        """Handle shop state transitions."""
        del modifiers

        from asterax.app.src.states.combat import CombatPhaseState
        from asterax.app.src.states.pause import PauseState

        if key == arcade.key.ESCAPE:
            self.state_machine.push_state(PauseState(self.state_machine))
        elif key == arcade.key.ENTER:
            self.state_machine.switch_state(CombatPhaseState(self.state_machine))
