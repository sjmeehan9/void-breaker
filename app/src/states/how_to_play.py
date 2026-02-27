"""How-to-play state."""

from __future__ import annotations

from typing import Final

import arcade
from asterax.app.src.input.input_manager import KEY_NAME_MAP, InputManager
from asterax.app.src.rendering.menu_renderer import MenuRenderer
from asterax.app.src.states.base_state import BaseState

_TITLE_TOP_OFFSET: Final[float] = 80.0
_CONTENT_TOP_OFFSET: Final[float] = 170.0
_CONTENT_BOTTOM_MARGIN: Final[float] = 80.0
_LINE_HEIGHT: Final[float] = 34.0
_SECTION_GAP: Final[float] = 22.0
_CONTROL_COLUMN_LEFT: Final[float] = 0.24
_CONTROL_COLUMN_RIGHT: Final[float] = 0.66
_ACTION_KEY_SEPARATOR: Final[str] = "::"
_KEY_CODE_TO_NAME: Final[dict[int, str]] = {
    code: name for name, code in KEY_NAME_MAP.items()
}


class HowToPlayState(BaseState):
    """How-to-play screen with dynamic key bindings and gameplay guidance."""

    _gameplay_sections: list[tuple[str, str]] = [
        (
            "Gameplay",
            "Destroy asteroids and enemies to earn currency. "
            "Collect currency crystals by flying over them.",
        ),
        (
            "Shop Loop",
            "Between levels, fly into shop nodes to purchase upgrades. "
            "Upgrades improve your weapons, defense, mobility, and economy.",
        ),
        (
            "Insurance",
            "Purchase insurance in the shop to protect your upgrades. "
            "Basic insurance retains half your upgrades on death. "
            "Premium retains all.",
        ),
        (
            "Tips",
            "- Keep moving to avoid concentrated fire.\n"
            "- Prioritize mobility upgrades early.\n"
            "- Collect currency quickly before it drifts away.",
        ),
    ]

    def __init__(self, state_machine) -> None:
        """Initialize renderer and scrolling state.

        Args:
            state_machine: Owning state machine instance.
        """
        super().__init__(state_machine)
        self._renderer = MenuRenderer()
        self._scroll_offset: float = 0.0
        self._max_scroll_offset: float = 0.0

    def on_enter(self) -> None:
        """Reset scroll state when entering the screen."""
        self._scroll_offset = 0.0
        self._max_scroll_offset = self._calculate_max_scroll()

    def on_draw(self) -> None:
        """Render controls, gameplay loop explanation, and tips."""
        window = arcade.get_window()
        center_x = window.width / 2
        self._renderer.draw_title(
            "How to Play", center_x, window.height - _TITLE_TOP_OFFSET
        )

        y = window.height - _CONTENT_TOP_OFFSET + self._scroll_offset
        y = self._draw_controls_section(y)
        y -= _SECTION_GAP
        y = self._draw_gameplay_sections(y)

        arcade.draw_text(
            "Up/Down: Scroll   ESC/Backspace: Back",
            center_x,
            24,
            (170, 190, 210, 255),
            18,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle scrolling and return-to-menu shortcuts.

        Args:
            key: Arcade key constant that was pressed.
            modifiers: Key modifier bitmask.
        """
        del modifiers

        from asterax.app.src.states.main_menu import MainMenuState

        if key in {arcade.key.ESCAPE, arcade.key.BACKSPACE, self._pause_key()}:
            self.state_machine.switch_state(MainMenuState(self.state_machine))
            return

        if key in {arcade.key.UP, arcade.key.W}:
            self._scroll_offset = min(self._scroll_offset + _LINE_HEIGHT * 1.5, 0.0)
            return

        if key in {arcade.key.DOWN, arcade.key.S}:
            self._scroll_offset = max(
                self._scroll_offset - _LINE_HEIGHT * 1.5,
                -self._max_scroll_offset,
            )

    def _build_controls_text(self) -> list[str]:
        """Build control rows from active input bindings.

        Returns:
            A list of serialized action/key rows using ``ACTION::KEY`` format.
        """
        rows: list[tuple[str, str]] = [
            ("Rotate Left", self._key_name_for_action("rotate_left")),
            ("Rotate Right", self._key_name_for_action("rotate_right")),
            ("Thrust", self._key_name_for_action("thrust")),
            ("Fire", self._key_name_for_action("fire")),
            ("Brake", self._key_name_for_action("brake")),
            ("Pause/Back", self._key_name_for_action("pause")),
        ]
        return [
            f"{action}{_ACTION_KEY_SEPARATOR}{bound_key}" for action, bound_key in rows
        ]

    def _draw_controls_section(self, start_y: float) -> float:
        """Render controls heading and two-column key binding rows.

        Args:
            start_y: Starting y-coordinate for this section.

        Returns:
            The y-coordinate after this section is drawn.
        """
        window = arcade.get_window()
        arcade.draw_text(
            "Controls",
            window.width * _CONTROL_COLUMN_LEFT,
            start_y,
            (255, 220, 80, 255),
            28,
            anchor_x="left",
        )

        y = start_y - (_LINE_HEIGHT + 8)
        for row in self._build_controls_text():
            action, key_label = row.split(_ACTION_KEY_SEPARATOR, maxsplit=1)
            arcade.draw_text(
                action,
                window.width * _CONTROL_COLUMN_LEFT,
                y,
                (210, 226, 240, 255),
                22,
                anchor_x="left",
            )
            arcade.draw_text(
                key_label,
                window.width * _CONTROL_COLUMN_RIGHT,
                y,
                (130, 220, 255, 255),
                22,
                anchor_x="left",
            )
            y -= _LINE_HEIGHT

        return y

    def _draw_gameplay_sections(self, start_y: float) -> float:
        """Render gameplay explanation, insurance details, and tips.

        Args:
            start_y: Starting y-coordinate for gameplay sections.

        Returns:
            The y-coordinate after all sections are drawn.
        """
        window = arcade.get_window()
        y = start_y

        for heading, body in self._gameplay_sections:
            arcade.draw_text(
                heading,
                window.width * _CONTROL_COLUMN_LEFT,
                y,
                (255, 220, 80, 255),
                28,
                anchor_x="left",
            )
            y -= _LINE_HEIGHT

            text_measure = arcade.Text(
                text=body,
                x=0,
                y=0,
                color=(210, 226, 240, 255),
                font_size=20,
                width=int(window.width * 0.58),
                multiline=True,
                align="left",
            )
            text_height = float(text_measure.content_height)
            arcade.draw_text(
                body,
                window.width * _CONTROL_COLUMN_LEFT,
                y,
                (210, 226, 240, 255),
                20,
                width=window.width * 0.58,
                multiline=True,
                align="left",
                anchor_x="left",
                anchor_y="top",
            )
            y -= text_height + 10.0

        return y

    def _calculate_max_scroll(self) -> float:
        """Calculate downward scroll budget required to reveal all content.

        Returns:
            Maximum downward scroll in pixels.
        """
        window = arcade.get_window()

        controls_height = (_LINE_HEIGHT + 8) + (
            len(self._build_controls_text()) * _LINE_HEIGHT
        )
        sections_height = 0.0
        for heading, body in self._gameplay_sections:
            sections_height += _LINE_HEIGHT
            text_measure = arcade.Text(
                text=body,
                x=0,
                y=0,
                color=(210, 226, 240, 255),
                font_size=20,
                width=int(window.width * 0.58),
                multiline=True,
                align="left",
            )
            sections_height += float(text_measure.content_height) + 10.0

        total_height = controls_height + _SECTION_GAP + sections_height
        available_height = window.height - _CONTENT_TOP_OFFSET - _CONTENT_BOTTOM_MARGIN
        return max(0.0, total_height - available_height)

    def _key_name_for_action(self, action: str) -> str:
        """Return a display string for the key bound to an action.

        Args:
            action: Input action name.

        Returns:
            Human-readable key label.
        """
        input_manager = self._input_manager()
        if input_manager is None:
            return "Unbound"

        key_code = input_manager.get_binding(action)
        if key_code < 0:
            return "Unbound"

        return self._format_key_label(key_code)

    def _format_key_label(self, key_code: int) -> str:
        """Format an Arcade key code into a concise UI label.

        Args:
            key_code: Arcade key constant.

        Returns:
            User-facing key label.
        """
        key_name = _KEY_CODE_TO_NAME.get(key_code, str(key_code))
        key_name = key_name.replace("_", " ")
        if key_name.startswith("KEY "):
            return key_name.replace("KEY ", "")
        return key_name.title()

    def _pause_key(self) -> int:
        """Return the configured pause key if available."""
        input_manager = self._input_manager()
        if input_manager is None:
            return -1
        return input_manager.get_binding("pause")

    def _input_manager(self) -> InputManager | None:
        """Return the active input manager if available on the game window."""
        window = arcade.get_window()
        input_manager = getattr(window, "input_manager", None)
        if isinstance(input_manager, InputManager):
            return input_manager
        return None
