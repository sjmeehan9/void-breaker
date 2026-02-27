"""Settings screen state."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

import arcade
from asterax.app.src.input.input_manager import KEY_NAME_MAP, InputManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.rendering.menu_renderer import MenuRenderer
from asterax.app.src.states.base_state import BaseState

_TITLE_TOP_OFFSET: Final[float] = 84.0
_ROW_START_OFFSET: Final[float] = 170.0
_ROW_HEIGHT: Final[float] = 36.0
_LEFT_MARGIN_RATIO: Final[float] = 0.12
_RIGHT_MARGIN_RATIO: Final[float] = 0.60
_SLIDER_STEPS: Final[int] = 10
_SLIDER_DELTA: Final[float] = 0.1
_STATUS_DURATION_SECONDS: Final[float] = 2.0
_DEFAULT_RETURN_TO: Final[str] = "main_menu"

_KEY_CODE_TO_NAME: Final[dict[int, str]] = {
    code: name for name, code in KEY_NAME_MAP.items()
}


class SettingType(Enum):
    """Supported settings row types."""

    HEADER = "header"
    SLIDER = "slider"
    TOGGLE = "toggle"
    MULTI_OPTION = "multi_option"
    KEYBIND = "keybind"
    ACTION = "action"


@dataclass(slots=True)
class SettingItem:
    """Single settings row definition."""

    name: str
    category: str
    item_type: SettingType
    key_in_settings: str | None = None
    options: tuple[str, ...] = ()
    action_name: str | None = None

    @property
    def selectable(self) -> bool:
        """Return whether the row is user-selectable."""
        return self.item_type is not SettingType.HEADER


class SettingsScreenState(BaseState):
    """Interactive settings screen with immediate persistence."""

    def __init__(self, state_machine, return_to: str = _DEFAULT_RETURN_TO) -> None:
        """Initialize settings state and UI state.

        Args:
            state_machine: Owning state machine instance.
            return_to: Target screen when leaving settings.
        """
        super().__init__(state_machine)
        self._renderer = MenuRenderer()
        self._return_to = return_to
        self._settings = GameSettings()
        self._settings_items: list[SettingItem] = self._build_settings_items()
        self._selected_index: int = 0
        self._is_rebinding: bool = False
        self._rebinding_action: str = ""
        self._status_message: str = ""
        self._status_timer: float = 0.0

    def on_enter(self) -> None:
        """Load persisted settings and set initial selected row."""
        self._settings = self._load_settings()
        self._selected_index = self._first_selectable_index()
        self._is_rebinding = False
        self._rebinding_action = ""
        self._clear_status()

    def on_update(self, delta_time: float) -> None:
        """Advance transient message timers.

        Args:
            delta_time: Elapsed frame time in seconds.
        """
        if self._status_timer <= 0.0:
            return
        self._status_timer = max(0.0, self._status_timer - delta_time)
        if self._status_timer == 0.0:
            self._status_message = ""

    def on_draw(self) -> None:
        """Render grouped settings with keyboard navigation hints."""
        window = arcade.get_window()
        center_x = window.width / 2
        self._renderer.draw_title(
            "Settings", center_x, window.height - _TITLE_TOP_OFFSET
        )

        left_x = window.width * _LEFT_MARGIN_RATIO
        right_x = window.width * _RIGHT_MARGIN_RATIO
        y = window.height - _ROW_START_OFFSET

        for index, item in enumerate(self._settings_items):
            is_selected = index == self._selected_index and not self._is_rebinding
            if item.item_type is SettingType.HEADER:
                arcade.draw_text(
                    item.name,
                    left_x,
                    y,
                    (255, 220, 80, 255),
                    20,
                    anchor_x="left",
                )
            else:
                row_color = (
                    (255, 235, 125, 255) if is_selected else (210, 226, 240, 255)
                )
                arcade.draw_text(item.name, left_x, y, row_color, 20, anchor_x="left")
                value_text = self._value_text(item)
                arcade.draw_text(value_text, right_x, y, row_color, 20, anchor_x="left")
            y -= _ROW_HEIGHT

        hint_text = "Up/Down: Navigate   Left/Right: Adjust   Enter: Select   ESC/Backspace: Back"
        arcade.draw_text(
            hint_text,
            center_x,
            52,
            (170, 190, 210, 255),
            16,
            anchor_x="center",
        )

        if self._status_message:
            arcade.draw_text(
                self._status_message,
                center_x,
                24,
                (255, 220, 80, 255),
                16,
                anchor_x="center",
            )

        if self._is_rebinding:
            self._draw_rebind_overlay()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle settings navigation and interaction controls.

        Args:
            key: Arcade key constant that was pressed.
            modifiers: Key modifier bitmask.
        """
        del modifiers

        if self._is_rebinding:
            if key == arcade.key.ESCAPE:
                self._is_rebinding = False
                self._rebinding_action = ""
                self._set_status("Rebind cancelled")
                return
            self._complete_rebind(key)
            return

        if key in {arcade.key.ESCAPE, arcade.key.BACKSPACE, self._pause_key()}:
            self._exit_settings()
            return
        if key in {arcade.key.UP, arcade.key.W}:
            self._move_selection(-1)
            return
        if key in {arcade.key.DOWN, arcade.key.S}:
            self._move_selection(1)
            return
        if key in {arcade.key.LEFT, arcade.key.A}:
            self._adjust_setting(-1)
            return
        if key in {arcade.key.RIGHT, arcade.key.D}:
            self._adjust_setting(1)
            return
        if key in {arcade.key.ENTER, arcade.key.SPACE}:
            current = self._settings_items[self._selected_index]
            if current.item_type is SettingType.KEYBIND:
                self._start_rebind()
            elif current.item_type is SettingType.TOGGLE:
                self._toggle_setting()
            elif current.item_type is SettingType.ACTION:
                self._reset_to_defaults()

    def _build_settings_items(self) -> list[SettingItem]:
        """Build ordered setting rows grouped by category."""
        return [
            SettingItem(
                name="Controls", category="controls", item_type=SettingType.HEADER
            ),
            SettingItem(
                name="Rotate Left",
                category="controls",
                item_type=SettingType.KEYBIND,
                key_in_settings="key_rotate_left",
                action_name="rotate_left",
            ),
            SettingItem(
                name="Rotate Right",
                category="controls",
                item_type=SettingType.KEYBIND,
                key_in_settings="key_rotate_right",
                action_name="rotate_right",
            ),
            SettingItem(
                name="Thrust",
                category="controls",
                item_type=SettingType.KEYBIND,
                key_in_settings="key_thrust",
                action_name="thrust",
            ),
            SettingItem(
                name="Fire",
                category="controls",
                item_type=SettingType.KEYBIND,
                key_in_settings="key_fire",
                action_name="fire",
            ),
            SettingItem(
                name="Brake",
                category="controls",
                item_type=SettingType.KEYBIND,
                key_in_settings="key_brake",
                action_name="brake",
            ),
            SettingItem(
                name="Special",
                category="controls",
                item_type=SettingType.KEYBIND,
                key_in_settings="key_special",
                action_name="special",
            ),
            SettingItem(
                name="Pause",
                category="controls",
                item_type=SettingType.KEYBIND,
                key_in_settings="key_pause",
                action_name="pause",
            ),
            SettingItem(name="Audio", category="audio", item_type=SettingType.HEADER),
            SettingItem(
                name="Master Volume",
                category="audio",
                item_type=SettingType.SLIDER,
                key_in_settings="master_volume",
            ),
            SettingItem(
                name="Music Volume",
                category="audio",
                item_type=SettingType.SLIDER,
                key_in_settings="music_volume",
            ),
            SettingItem(
                name="SFX Volume",
                category="audio",
                item_type=SettingType.SLIDER,
                key_in_settings="sfx_volume",
            ),
            SettingItem(name="Visual", category="visual", item_type=SettingType.HEADER),
            SettingItem(
                name="Colorblind Mode",
                category="visual",
                item_type=SettingType.TOGGLE,
                key_in_settings="colorblind_mode",
            ),
            SettingItem(
                name="Screen Shake",
                category="visual",
                item_type=SettingType.MULTI_OPTION,
                key_in_settings="screen_shake",
                options=("off", "low", "medium"),
            ),
            SettingItem(
                name="Gameplay", category="gameplay", item_type=SettingType.HEADER
            ),
            SettingItem(
                name="Fire Mode",
                category="gameplay",
                item_type=SettingType.MULTI_OPTION,
                key_in_settings="fire_mode",
                options=("hold", "tap"),
            ),
            SettingItem(
                name="Autofire",
                category="gameplay",
                item_type=SettingType.TOGGLE,
                key_in_settings="autofire",
            ),
            SettingItem(
                name="Difficulty",
                category="gameplay",
                item_type=SettingType.MULTI_OPTION,
                key_in_settings="difficulty",
                options=("casual", "classic", "hard"),
            ),
            SettingItem(name="System", category="system", item_type=SettingType.HEADER),
            SettingItem(
                name="Reset to Defaults",
                category="system",
                item_type=SettingType.ACTION,
            ),
        ]

    def _move_selection(self, direction: int) -> None:
        """Move highlight to the previous or next selectable row.

        Args:
            direction: -1 for up, +1 for down.
        """
        selectable_indexes = [
            index for index, item in enumerate(self._settings_items) if item.selectable
        ]
        current_pos = selectable_indexes.index(self._selected_index)
        next_pos = (current_pos + direction) % len(selectable_indexes)
        self._selected_index = selectable_indexes[next_pos]

    def _adjust_setting(self, direction: int) -> None:
        """Adjust value-based settings with left/right input.

        Args:
            direction: -1 for decrement, +1 for increment.
        """
        item = self._settings_items[self._selected_index]
        if item.key_in_settings is None:
            return

        if item.item_type is SettingType.SLIDER:
            current_value = float(getattr(self._settings, item.key_in_settings))
            adjusted = max(
                0.0,
                min(1.0, round(current_value + (direction * _SLIDER_DELTA), 1)),
            )
            if adjusted == current_value:
                return
            setattr(self._settings, item.key_in_settings, adjusted)
            self._save_settings()
            self._play_feedback_sound()
            return

        if item.item_type is SettingType.MULTI_OPTION and item.options:
            current_value = str(getattr(self._settings, item.key_in_settings))
            try:
                current_index = item.options.index(current_value)
            except ValueError:
                current_index = 0
            next_index = (current_index + direction) % len(item.options)
            setattr(self._settings, item.key_in_settings, item.options[next_index])
            self._save_settings()
            return

        if item.item_type is SettingType.TOGGLE:
            self._toggle_setting()

    def _toggle_setting(self) -> None:
        """Flip a boolean setting and persist it immediately."""
        item = self._settings_items[self._selected_index]
        if item.item_type is not SettingType.TOGGLE or item.key_in_settings is None:
            return
        current_value = bool(getattr(self._settings, item.key_in_settings))
        setattr(self._settings, item.key_in_settings, not current_value)
        self._save_settings()

    def _start_rebind(self) -> None:
        """Enter key-rebinding mode for the selected keybind row."""
        item = self._settings_items[self._selected_index]
        if item.item_type is not SettingType.KEYBIND or item.action_name is None:
            return
        self._is_rebinding = True
        self._rebinding_action = item.action_name
        self._set_status(f"Press a key for {item.name}")

    def _complete_rebind(self, key: int) -> None:
        """Capture a rebound key, clearing duplicate mappings.

        Args:
            key: Newly selected Arcade key code.
        """
        setting_key = self._settings_key_for_action(self._rebinding_action)
        key_name = _KEY_CODE_TO_NAME.get(key)
        if setting_key is None or key_name is None:
            self._set_status("Unsupported key")
            self._is_rebinding = False
            self._rebinding_action = ""
            return

        for candidate_key in self._all_key_setting_fields():
            existing = str(getattr(self._settings, candidate_key))
            if existing == key_name and candidate_key != setting_key:
                setattr(self._settings, candidate_key, "UNBOUND")
                self._set_status(
                    f"{key_name} unbound from {self._action_label(candidate_key)}"
                )
                break

        setattr(self._settings, setting_key, key_name)
        self._save_settings()

        self._is_rebinding = False
        self._rebinding_action = ""

    def _save_settings(self) -> None:
        """Persist current settings and hot-apply to active systems."""
        window = arcade.get_window()
        persistence = getattr(window, "persistence", None)
        if persistence is not None and hasattr(persistence, "save_settings"):
            persistence.save_settings(self._settings)

        input_manager = getattr(window, "input_manager", None)
        if isinstance(input_manager, InputManager):
            input_manager.update_bindings(self._settings)

        audio_manager = getattr(window, "audio_manager", None)
        if audio_manager is not None and hasattr(audio_manager, "update_settings"):
            audio_manager.update_settings(self._settings)

        update_runtime_settings = getattr(window, "update_runtime_settings", None)
        if callable(update_runtime_settings):
            update_runtime_settings(self._settings)

    def _reset_to_defaults(self) -> None:
        """Restore factory defaults and persist immediately."""
        self._settings = GameSettings()
        self._save_settings()
        self._set_status("Settings reset to defaults")

    def _load_settings(self) -> GameSettings:
        """Load current settings from persistence or use defaults."""
        window = arcade.get_window()
        persistence = getattr(window, "persistence", None)
        if persistence is not None and hasattr(persistence, "load_settings"):
            loaded = persistence.load_settings()
            if isinstance(loaded, GameSettings):
                return loaded
        return GameSettings()

    def _first_selectable_index(self) -> int:
        """Return the first selectable row index."""
        for index, item in enumerate(self._settings_items):
            if item.selectable:
                return index
        return 0

    def _value_text(self, item: SettingItem) -> str:
        """Return the display value text for a settings row.

        Args:
            item: Settings row descriptor.

        Returns:
            UI-ready value label.
        """
        if item.item_type is SettingType.ACTION:
            return "Press Enter"

        if item.key_in_settings is None:
            return ""
        value = getattr(self._settings, item.key_in_settings)

        if item.item_type is SettingType.SLIDER:
            as_float = float(value)
            filled = int(round(as_float * _SLIDER_STEPS))
            empty = _SLIDER_STEPS - filled
            return f"[{'=' * filled}{' ' * empty}] {int(as_float * 100)}%"

        if item.item_type is SettingType.TOGGLE:
            return "On" if bool(value) else "Off"

        if item.item_type is SettingType.MULTI_OPTION:
            return str(value).title()

        if item.item_type is SettingType.KEYBIND:
            return self._format_key_name(str(value))

        return ""

    def _format_key_name(self, key_name: str) -> str:
        """Convert persisted key string into a concise label.

        Args:
            key_name: Persisted key string value.

        Returns:
            Human-readable key label.
        """
        if key_name == "UNBOUND":
            return "Unbound"
        normalized = key_name.replace("KEY_", "")
        return normalized.replace("_", " ").title()

    def _settings_key_for_action(self, action: str) -> str | None:
        """Resolve a keybind action into its settings field name."""
        mapping = {
            "rotate_left": "key_rotate_left",
            "rotate_right": "key_rotate_right",
            "thrust": "key_thrust",
            "fire": "key_fire",
            "brake": "key_brake",
            "special": "key_special",
            "pause": "key_pause",
        }
        return mapping.get(action)

    def _all_key_setting_fields(self) -> tuple[str, ...]:
        """Return all settings fields storing key bindings."""
        return (
            "key_rotate_left",
            "key_rotate_right",
            "key_thrust",
            "key_fire",
            "key_brake",
            "key_special",
            "key_pause",
        )

    def _action_label(self, setting_key: str) -> str:
        """Return a user-facing label for a key setting field."""
        labels = {
            "key_rotate_left": "Rotate Left",
            "key_rotate_right": "Rotate Right",
            "key_thrust": "Thrust",
            "key_fire": "Fire",
            "key_brake": "Brake",
            "key_special": "Special",
            "key_pause": "Pause",
        }
        return labels.get(setting_key, setting_key)

    def _play_feedback_sound(self) -> None:
        """Play a subtle UI feedback sound when available."""
        audio_manager = getattr(arcade.get_window(), "audio_manager", None)
        if audio_manager is not None and hasattr(audio_manager, "play"):
            audio_manager.play("menu_nav")

    def _draw_rebind_overlay(self) -> None:
        """Render modal prompt while waiting for key rebind input."""
        window = arcade.get_window()
        arcade.draw_lrbt_rectangle_filled(
            0, window.width, 0, window.height, (0, 0, 0, 150)
        )
        label = self._rebinding_action.replace("_", " ").title()
        arcade.draw_text(
            f"Press a key for {label} (ESC to cancel)",
            window.width / 2,
            window.height / 2,
            (230, 245, 255, 255),
            24,
            anchor_x="center",
            anchor_y="center",
        )

    def _set_status(self, message: str) -> None:
        """Set transient status text.

        Args:
            message: Message shown at the bottom of the screen.
        """
        self._status_message = message
        self._status_timer = _STATUS_DURATION_SECONDS

    def _clear_status(self) -> None:
        """Clear transient status text."""
        self._status_message = ""
        self._status_timer = 0.0

    def _pause_key(self) -> int:
        """Return the current pause binding from the input manager."""
        input_manager = getattr(arcade.get_window(), "input_manager", None)
        if isinstance(input_manager, InputManager):
            return input_manager.get_binding("pause")
        return -1

    def _exit_settings(self) -> None:
        """Return to the configured parent screen."""
        if self._return_to == "pause":
            self.state_machine.pop_state()
            return

        from asterax.app.src.states.main_menu import MainMenuState

        self.state_machine.switch_state(MainMenuState(self.state_machine))
