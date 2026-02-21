"""Game initialization state."""

import arcade
from asterax.app.src.states.base_state import BaseState


class GameInitState(BaseState):
    """Short pass-through state before entering combat."""

    def on_enter(self) -> None:
        """Immediately transition to combat in phase 1."""
        from asterax.app.src.states.combat import CombatPhaseState

        self.state_machine.switch_state(CombatPhaseState(self.state_machine))

    def on_draw(self) -> None:
        """Render temporary initialization text."""
        window = arcade.get_window()
        arcade.draw_text(
            "Initializing...",
            window.width / 2,
            window.height / 2,
            arcade.color.WHITE,
            36,
            anchor_x="center",
        )
