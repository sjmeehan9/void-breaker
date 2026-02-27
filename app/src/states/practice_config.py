"""Practice mode configuration state."""

from __future__ import annotations

import arcade
from asterax.app.src.config.difficulty_tables import get_difficulty_params
from asterax.app.src.config.game_config import DifficultyParams
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.rendering.menu_renderer import MenuRenderer
from asterax.app.src.states.base_state import BaseState


class PracticeConfigState(BaseState):
    """Configure and launch practice/training mode."""

    def __init__(self, state_machine) -> None:
        """Initialize practice toggle state and navigation cursor.

        Args:
            state_machine: Owning state machine instance.
        """
        super().__init__(state_machine)
        self._toggles: dict[str, bool] = {
            "asteroids_only": True,
            "infinite_shields": True,
            "reduced_count": True,
        }
        self._rows: list[str] = [
            "asteroids_only",
            "infinite_shields",
            "reduced_count",
            "start_practice",
            "back",
        ]
        self._labels: dict[str, str] = {
            "asteroids_only": "Asteroids Only",
            "infinite_shields": "Infinite Shields",
            "reduced_count": "Reduced Count",
            "start_practice": "Start Practice",
            "back": "Back",
        }
        self._selected_index = 0
        self._renderer = MenuRenderer()

    def on_draw(self) -> None:
        """Render heading, toggle rows, and controls hint."""
        window = arcade.get_window()
        center_x = window.width / 2
        center_y = window.height / 2

        self._renderer.draw_title("Practice Mode", center_x, center_y + 220)

        options: list[str] = []
        for row in self._rows:
            if row in self._toggles:
                status = "ON" if self._toggles[row] else "OFF"
                options.append(f"{self._labels[row]} [{status}]")
            else:
                options.append(self._labels[row])

        self._renderer.draw_menu_options(
            options=options,
            selected=self._selected_index,
            x=center_x,
            y=center_y + 70,
            spacing=54.0,
        )

        arcade.draw_text(
            "Up/Down: Navigate  Enter/Space: Toggle or Select  Esc: Back",
            center_x,
            center_y - 150,
            (190, 210, 225),
            16,
            anchor_x="center",
        )
        arcade.draw_text(
            "Practice skips shop and leaderboard score recording.",
            center_x,
            center_y - 182,
            (170, 190, 210),
            14,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle navigation, toggling, and launch actions."""
        del modifiers
        if key in self._up_keys():
            self._selected_index = (self._selected_index - 1) % len(self._rows)
            self._play_menu_sound("menu_nav")
            return

        if key in self._down_keys():
            self._selected_index = (self._selected_index + 1) % len(self._rows)
            self._play_menu_sound("menu_nav")
            return

        if key == arcade.key.ESCAPE:
            self._back_to_menu()
            return

        if key not in self._select_keys():
            return

        selected_row = self._rows[self._selected_index]
        if selected_row in self._toggles:
            self._toggle_item(selected_row)
            self._play_menu_sound("menu_select")
            return
        if selected_row == "start_practice":
            self._play_menu_sound("menu_select")
            self._start_practice()
            return
        self._play_menu_sound("menu_nav")
        self._back_to_menu()

    def _toggle_item(self, key: str) -> None:
        """Flip a practice toggle by key.

        Args:
            key: Toggle identifier in `_toggles`.
        """
        if key not in self._toggles:
            return
        self._toggles[key] = not self._toggles[key]

    def _build_practice_params(self) -> DifficultyParams:
        """Build Level-1 practice params from current settings and toggles."""
        params = get_difficulty_params(1)

        if self._toggles["asteroids_only"]:
            params.enemy_spawn_enabled = False
            params.enemy_count_max = 0
            params.enemy_aggression = 0.0
            params.aggressive_ratio = 0.0
            params.enemy_spawn_interval = 99.0

        if self._toggles["reduced_count"]:
            params.asteroid_count = max(1, int(round(params.asteroid_count * 0.5)))

        return params

    def _start_practice(self) -> None:
        """Launch CombatPhase in practice mode with selected toggles."""
        from asterax.app.src.states.combat import CombatPhaseState

        practice_params = self._build_practice_params()
        self.state_machine.switch_state(
            CombatPhaseState(
                self.state_machine,
                is_practice=True,
                practice_asteroids_only=self._toggles["asteroids_only"],
                practice_infinite_shields=self._toggles["infinite_shields"],
                practice_reduced_count=self._toggles["reduced_count"],
                practice_params_override=practice_params,
            )
        )

    def _back_to_menu(self) -> None:
        """Return to main menu while preserving menu highlight on Practice."""
        from asterax.app.src.states.main_menu import MainMenuState

        self.state_machine.switch_state(MainMenuState(self.state_machine, 1))

    def _input_manager(self) -> InputManager | None:
        """Return typed input manager when available."""
        window = arcade.get_window()
        input_manager = getattr(window, "input_manager", None)
        if isinstance(input_manager, InputManager):
            return input_manager
        return None

    def _up_keys(self) -> set[int]:
        """Return keys accepted for upward list navigation."""
        keys = {arcade.key.UP, arcade.key.W}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("thrust"))
        return keys

    def _down_keys(self) -> set[int]:
        """Return keys accepted for downward list navigation."""
        keys = {arcade.key.DOWN, arcade.key.S}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("brake"))
        return keys

    def _select_keys(self) -> set[int]:
        """Return keys accepted for row activation."""
        keys = {arcade.key.ENTER, arcade.key.SPACE}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("fire"))
        return keys

    def _play_menu_sound(self, sound_name: str) -> None:
        """Play menu SFX through the active audio manager when available."""
        window = arcade.get_window()
        audio_manager = getattr(window, "audio_manager", None)
        if audio_manager is not None:
            audio_manager.play(sound_name)
