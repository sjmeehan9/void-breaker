"""Pause overlay state implementation."""

from __future__ import annotations

from typing import Final

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.rendering.menu_renderer import MenuRenderer
from asterax.app.src.states.base_state import BaseState

_TITLE_TOP_OFFSET: Final[float] = 150.0
_OPTIONS_START_OFFSET: Final[float] = 30.0
_OPTIONS_SPACING: Final[float] = 56.0


class PauseState(BaseState):
    """Overlay pause menu for combat and shop phases."""

    def __init__(self, state_machine) -> None:
        """Initialize pause menu state and navigation cursor.

        Args:
            state_machine: Owning state machine instance.
        """
        super().__init__(state_machine)
        self._renderer = MenuRenderer()
        self._menu_options: list[tuple[str, str]] = [
            ("Resume", "resume"),
            ("Restart Run", "restart"),
            ("Settings", "settings"),
            ("Exit to Menu", "menu"),
        ]
        self._selected_index: int = 0

    def on_enter(self) -> None:
        """Reset selected option when pause overlay opens."""
        self._selected_index = 0

    def on_draw(self) -> None:
        """Draw dimmed overlay and pause menu options."""
        window = arcade.get_window()
        center_x = window.width / 2
        center_y = window.height / 2

        self._draw_overlay()
        self._renderer.draw_title("Paused", center_x, center_y + _TITLE_TOP_OFFSET)
        self._renderer.draw_menu_options(
            options=[option[0] for option in self._menu_options],
            selected=self._selected_index,
            x=center_x,
            y=center_y + _OPTIONS_START_OFFSET,
            spacing=_OPTIONS_SPACING,
        )
        arcade.draw_text(
            "Up/Down: Navigate   Enter: Select   Pause: Resume",
            center_x,
            52,
            (170, 190, 210, 255),
            16,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle pause menu navigation and actions.

        Args:
            key: Arcade key code that was pressed.
            modifiers: Key modifier bitmask.
        """
        del modifiers

        if key == self._pause_key() or key == arcade.key.ESCAPE:
            self._resume()
            return
        if key in {arcade.key.UP, arcade.key.W}:
            self._navigate(-1)
            return
        if key in {arcade.key.DOWN, arcade.key.S}:
            self._navigate(1)
            return
        if key in {arcade.key.ENTER, arcade.key.SPACE}:
            self._select()

    def _draw_overlay(self) -> None:
        """Render a semi-transparent dark fullscreen overlay."""
        window = arcade.get_window()
        arcade.draw_lrbt_rectangle_filled(
            0.0,
            float(window.width),
            0.0,
            float(window.height),
            (0, 0, 0, 170),
        )

    def _navigate(self, direction: int) -> None:
        """Move menu selection with wrap-around.

        Args:
            direction: -1 for up or +1 for down.
        """
        option_count = len(self._menu_options)
        self._selected_index = (self._selected_index + direction) % option_count

    def _select(self) -> None:
        """Dispatch selected pause action."""
        action = self._menu_options[self._selected_index][1]
        if action == "resume":
            self._resume()
            return
        if action == "restart":
            self._restart()
            return
        if action == "settings":
            self._open_settings()
            return
        self._exit_to_menu()

    def _resume(self) -> None:
        """Resume gameplay by popping the pause overlay."""
        self.state_machine.pop_state()

    def _restart(self) -> None:
        """Restart the run by switching to game initialization."""
        from asterax.app.src.states.game_init import GameInitState

        self.state_machine.switch_state(GameInitState(self.state_machine))

    def _open_settings(self) -> None:
        """Open settings as an overlay above pause and return back to pause."""
        from asterax.app.src.states.settings_screen import SettingsScreenState

        self.state_machine.push_state(
            SettingsScreenState(self.state_machine, return_to="pause")
        )

    def _exit_to_menu(self) -> None:
        """Discard current run and return to main menu."""
        from asterax.app.src.states.main_menu import MainMenuState

        self.state_machine.switch_state(MainMenuState(self.state_machine))

    def _pause_key(self) -> int:
        """Return current configured pause key binding."""
        input_manager = getattr(arcade.get_window(), "input_manager", None)
        if isinstance(input_manager, InputManager):
            return input_manager.get_binding("pause")
        return arcade.key.ESCAPE
