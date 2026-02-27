"""Main menu state."""

from __future__ import annotations

from typing import ClassVar

import arcade
from asterax.app.src.config.difficulty_tables import (
    DifficultyPreset,
    parse_difficulty_preset,
)
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.rendering.menu_renderer import MenuRenderer
from asterax.app.src.states.base_state import BaseState


class MainMenuState(BaseState):
    """Interactive main menu with keyboard navigation and transitions."""

    _last_selected_index: ClassVar[int] = 0

    def __init__(
        self,
        state_machine,
        initial_selection: int | None = None,
    ) -> None:
        """Initialize menu state and optional starting selection.

        Args:
            state_machine: Owning state machine instance.
            initial_selection: Optional index to use instead of the persisted one.
        """
        super().__init__(state_machine)
        self._menu_options: list[tuple[str, str]] = [
            ("New Game", "new_game"),
            ("Practice", "practice"),
            ("How to Play", "how_to_play"),
            ("Settings", "settings"),
            ("High Scores", "high_scores"),
            ("Quit", "quit"),
        ]
        self._selected_index = initial_selection
        self._fade_alpha: float = 255.0
        self._fade_speed: float = 850.0
        self._fading_in: bool = True
        self._pending_target: str | None = None
        self._showing_difficulty_selection = False
        self._difficulty_options: list[DifficultyPreset] = [
            DifficultyPreset.CASUAL,
            DifficultyPreset.CLASSIC,
            DifficultyPreset.HARD,
        ]
        self._difficulty_descriptions: dict[DifficultyPreset, str] = {
            DifficultyPreset.CASUAL: "Fewer asteroids, slower enemies, more drops",
            DifficultyPreset.CLASSIC: "Balanced default challenge",
            DifficultyPreset.HARD: "More pressure, fewer drops, heavier damage",
        }
        self._difficulty_selected_index = 1
        self._renderer = MenuRenderer()

    def on_enter(self) -> None:
        """Reset transition animation state on menu entry."""
        if self._selected_index is None:
            self._selected_index = self._clamp_index(MainMenuState._last_selected_index)
        else:
            self._selected_index = self._clamp_index(self._selected_index)

        self._fade_alpha = 255.0
        self._fading_in = True
        self._pending_target = None
        self._showing_difficulty_selection = False
        self._difficulty_selected_index = self._load_selected_difficulty_index()

    def on_exit(self) -> None:
        """Persist the current selected index for later menu returns."""
        MainMenuState._last_selected_index = self._selected_index

    def on_update(self, delta_time: float) -> None:
        """Advance fade-in/fade-out animation state.

        Args:
            delta_time: Time elapsed since the previous update in seconds.
        """
        fade_delta = self._fade_speed * delta_time

        if self._fading_in:
            self._fade_alpha = max(0.0, self._fade_alpha - fade_delta)
            if self._fade_alpha <= 0.0:
                self._fading_in = False

        if self._pending_target is not None:
            self._fade_alpha = min(255.0, self._fade_alpha + fade_delta)
            if self._fade_alpha >= 255.0:
                self._activate_target(self._pending_target)
                self._pending_target = None

    def on_draw(self) -> None:
        """Draw title and menu option list with selection highlight."""
        window = arcade.get_window()
        center_x = window.width / 2
        center_y = window.height / 2

        self._renderer.draw_title("VoidBreaker", center_x, center_y + 200)
        self._renderer.draw_menu_options(
            options=[option[0] for option in self._menu_options],
            selected=self._selected_index,
            x=center_x,
            y=center_y + 40,
            spacing=58.0,
        )

        if self._showing_difficulty_selection:
            self._draw_difficulty_prompt()

        if self._fade_alpha > 0.0:
            arcade.draw_lrbt_rectangle_filled(
                0.0,
                float(window.width),
                0.0,
                float(window.height),
                (0, 0, 0, int(self._fade_alpha)),
            )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle menu navigation and option selection.

        Args:
            key: Arcade key constant that was pressed.
            modifiers: Key modifier bitmask.
        """
        del modifiers
        if self._pending_target is not None:
            return

        if self._showing_difficulty_selection:
            self._handle_difficulty_selection_input(key)
            return

        if key in self._up_keys():
            self._navigate(-1)
            return

        if key in self._down_keys():
            self._navigate(1)
            return

        if key in self._select_keys():
            self._select()

    def _navigate(self, direction: int) -> None:
        """Move highlighted option by one step with wrap-around.

        Args:
            direction: Direction delta, negative for up and positive for down.
        """
        option_count = len(self._menu_options)
        self._selected_index = (self._selected_index + direction) % option_count
        MainMenuState._last_selected_index = self._selected_index
        self._play_menu_sound("menu_nav")

    def _select(self) -> None:
        """Queue activation of the highlighted option after fade-out."""
        MainMenuState._last_selected_index = self._selected_index
        selected_target = self._menu_options[self._selected_index][1]
        if selected_target == "new_game":
            self._show_difficulty_selection()
            return
        self._pending_target = selected_target
        self._play_menu_sound("menu_select")

    def _activate_target(self, target: str) -> None:
        """Execute the transition action for a selected menu item.

        Args:
            target: Internal target identifier from menu options.
        """
        if target == "new_game":
            from asterax.app.src.states.game_init import GameInitState

            self.state_machine.switch_state(GameInitState(self.state_machine))
            return

        if target == "how_to_play":
            from asterax.app.src.states.how_to_play import HowToPlayState

            self.state_machine.switch_state(HowToPlayState(self.state_machine))
            return

        if target == "practice":
            from asterax.app.src.states.practice_config import PracticeConfigState

            self.state_machine.switch_state(PracticeConfigState(self.state_machine))
            return

        if target == "settings":
            from asterax.app.src.states.settings_screen import SettingsScreenState

            self.state_machine.switch_state(SettingsScreenState(self.state_machine))
            return

        if target == "high_scores":
            from asterax.app.src.states.high_scores import HighScoresState

            self.state_machine.switch_state(HighScoresState(self.state_machine))
            return

        if target == "quit":
            window = arcade.get_window()
            window.close()

    def _play_menu_sound(self, sound_name: str) -> None:
        """Play a menu sound effect if the window has an audio manager.

        Args:
            sound_name: Sound identifier in the audio manager.
        """
        window = arcade.get_window()
        audio_manager = getattr(window, "audio_manager", None)
        if audio_manager is not None:
            audio_manager.play(sound_name)

    def _show_difficulty_selection(self) -> None:
        """Enter New Game difficulty selection mode."""
        self._showing_difficulty_selection = True
        self._difficulty_selected_index = self._load_selected_difficulty_index()
        self._play_menu_sound("menu_select")

    def _handle_difficulty_selection_input(self, key: int) -> None:
        """Handle input while difficulty selection prompt is active."""
        if key in self._up_keys():
            self._difficulty_selected_index = (
                self._difficulty_selected_index - 1
            ) % len(self._difficulty_options)
            self._play_menu_sound("menu_nav")
            return

        if key in self._down_keys():
            self._difficulty_selected_index = (
                self._difficulty_selected_index + 1
            ) % len(self._difficulty_options)
            self._play_menu_sound("menu_nav")
            return

        if key in self._select_keys():
            self._persist_selected_difficulty()
            self._showing_difficulty_selection = False
            self._pending_target = "new_game"
            self._play_menu_sound("menu_select")
            return

        if key == arcade.key.ESCAPE:
            self._showing_difficulty_selection = False
            self._play_menu_sound("menu_nav")

    def _load_selected_difficulty_index(self) -> int:
        """Return selected difficulty index from persisted settings."""
        window = arcade.get_window()
        persistence = getattr(window, "persistence", None)
        if persistence is None or not hasattr(persistence, "load_settings"):
            return 1
        settings = persistence.load_settings()
        difficulty = parse_difficulty_preset(getattr(settings, "difficulty", "classic"))
        return self._difficulty_options.index(difficulty)

    def _persist_selected_difficulty(self) -> None:
        """Persist selected difficulty to settings storage."""
        selected = self._difficulty_options[self._difficulty_selected_index].value
        window = arcade.get_window()
        persistence = getattr(window, "persistence", None)
        if persistence is None:
            return

        loaded_settings: GameSettings
        if hasattr(persistence, "load_settings"):
            loaded_settings = persistence.load_settings()
        else:
            loaded_settings = GameSettings()
        loaded_settings.difficulty = selected
        if hasattr(persistence, "save_settings"):
            persistence.save_settings(loaded_settings)
        if hasattr(window, "runtime_settings"):
            window.runtime_settings = loaded_settings

    def _draw_difficulty_prompt(self) -> None:
        """Draw New Game difficulty prompt overlay."""
        window = arcade.get_window()
        center_x = window.width / 2
        center_y = window.height / 2

        arcade.draw_lrbt_rectangle_filled(
            center_x - 330,
            center_x + 330,
            center_y - 220,
            center_y + 220,
            (8, 12, 24, 230),
        )
        self._renderer.draw_title("Select Difficulty", center_x, center_y + 165)

        option_labels = [preset.value.title() for preset in self._difficulty_options]
        self._renderer.draw_menu_options(
            options=option_labels,
            selected=self._difficulty_selected_index,
            x=center_x,
            y=center_y + 70,
            spacing=52.0,
        )

        selected_preset = self._difficulty_options[self._difficulty_selected_index]
        arcade.draw_text(
            self._difficulty_descriptions[selected_preset],
            center_x,
            center_y - 80,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
        )
        arcade.draw_text(
            "Enter: Confirm   Esc: Back",
            center_x,
            center_y - 135,
            arcade.color.GRAY,
            16,
            anchor_x="center",
        )

    def _up_keys(self) -> set[int]:
        """Return supported key bindings for upward menu navigation."""
        keys = {arcade.key.UP, arcade.key.W}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("thrust"))
        return keys

    def _down_keys(self) -> set[int]:
        """Return supported key bindings for downward menu navigation."""
        keys = {arcade.key.DOWN, arcade.key.S}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("brake"))
        return keys

    def _select_keys(self) -> set[int]:
        """Return supported key bindings for selecting a menu option."""
        keys = {arcade.key.ENTER, arcade.key.SPACE}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("fire"))
        return keys

    def _input_manager(self) -> InputManager | None:
        """Return the active input manager if available on the game window."""
        window = arcade.get_window()
        input_manager = getattr(window, "input_manager", None)
        if isinstance(input_manager, InputManager):
            return input_manager
        return None

    def _clamp_index(self, index: int) -> int:
        """Clamp an index into the current menu option range.

        Args:
            index: Candidate menu index.

        Returns:
            A valid index into the menu option list.
        """
        if not self._menu_options:
            return 0
        return max(0, min(index, len(self._menu_options) - 1))
