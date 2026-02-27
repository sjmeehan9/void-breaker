"""Game-over state with run summary, optional name entry, and replay options."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

import arcade
from asterax.app.src.config.game_config import GAME_CONFIG, InsuranceTier
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.schemas import HighScoreEntry
from asterax.app.src.rendering.menu_renderer import MenuRenderer
from asterax.app.src.states.base_state import BaseState

if TYPE_CHECKING:
    from asterax.app.src.persistence.persistence_manager import PersistenceManager
    from asterax.app.src.states.state_machine import StateMachine
    from asterax.app.src.window import VoidBreakerWindow


@dataclass(slots=True)
class RunSummary:
    """Renderable run-summary values for the game-over screen."""

    score: int = 0
    level_reached: int = 1
    currency_collected: int = 0
    currency_spent: int = 0
    currency_balance: int = 0
    enemies_destroyed: int = 0
    asteroids_destroyed: int = 0
    insurance_tier: str = InsuranceTier.OFF.value


class GameOverPhase(StrEnum):
    """Sub-phase identifiers for the game-over flow."""

    SUMMARY = "summary"
    NAME_ENTRY = "name_entry"
    OPTIONS = "options"


class GameOverState(BaseState):
    """Game-over screen with summary, optional high-score entry, and menu options."""

    def __init__(
        self,
        state_machine: StateMachine,
        run_stats: dict[str, int] | None = None,
        persistence: PersistenceManager | None = None,
        is_practice: bool = False,
    ) -> None:
        """Store run stats payload and optional persistence override.

        Args:
            state_machine: Owning state machine instance.
            run_stats: Optional run-summary payload from combat.
            persistence: Optional persistence manager override for testing.
        """
        super().__init__(state_machine)
        self.run_summary = RunSummary()
        self._phase = GameOverPhase.SUMMARY
        self._qualifies_for_leaderboard = False
        self._has_saved_high_score = False
        self._name_buffer = ""
        self._name_min_length = 3
        self._name_max_length = 10
        self._summary_elapsed_seconds = 0.0
        self._summary_min_seconds = 0.6
        self._options: list[str] = ["Play Again", "Return to Menu"]
        self._selected_option_index = 0
        self._cursor_blink_seconds = 0.0
        self._cursor_visible = True
        self._cursor_toggle_period = 0.45
        self._renderer = MenuRenderer()
        self._run_stats_payload = run_stats or {}
        self._persistence = persistence
        self._is_practice = bool(is_practice)

    def on_enter(self) -> None:
        """Hydrate run summary values and evaluate leaderboard qualification."""
        self.run_summary = RunSummary(
            score=int(self._run_stats_payload.get("score", 0)),
            level_reached=max(1, int(self._run_stats_payload.get("level_reached", 1))),
            currency_collected=int(
                self._run_stats_payload.get("currency_collected", 0)
            ),
            currency_spent=int(self._run_stats_payload.get("currency_spent", 0)),
            currency_balance=int(self._run_stats_payload.get("currency_balance", 0)),
            enemies_destroyed=int(self._run_stats_payload.get("enemies_destroyed", 0)),
            asteroids_destroyed=int(
                self._run_stats_payload.get("asteroids_destroyed", 0)
            ),
            insurance_tier=str(
                self._run_stats_payload.get("insurance_tier", InsuranceTier.OFF.value)
            ).lower(),
        )

        self._summary_elapsed_seconds = 0.0
        self._cursor_blink_seconds = 0.0
        self._cursor_visible = True
        self._name_buffer = ""
        self._has_saved_high_score = False
        self._selected_option_index = 0

        self._play_sound("game_over")
        if self._is_practice:
            self._qualifies_for_leaderboard = False
            return
        persistence = self._resolve_persistence()
        if persistence is None:
            return
        high_scores = persistence.load_high_scores()
        self._qualifies_for_leaderboard = self._check_qualification(high_scores)

    def _resolve_persistence(self) -> PersistenceManager | None:
        """Return explicit or window-backed persistence manager when available."""
        if self._persistence is not None:
            return self._persistence
        window = arcade.get_window()
        if window is None:
            return None
        return getattr(window, "persistence", None)

    def on_update(self, delta_time: float) -> None:
        """Advance summary delay and cursor blink timers.

        Args:
            delta_time: Elapsed frame time in seconds.
        """
        if self._phase is GameOverPhase.SUMMARY:
            self._summary_elapsed_seconds += max(0.0, delta_time)

        if self._phase is GameOverPhase.NAME_ENTRY:
            self._cursor_blink_seconds += max(0.0, delta_time)
            if self._cursor_blink_seconds >= self._cursor_toggle_period:
                self._cursor_blink_seconds = 0.0
                self._cursor_visible = not self._cursor_visible

    def on_draw(self) -> None:
        """Render game-over summary, name-entry prompt, and options menu."""
        window = arcade.get_window()
        center_x = window.width / 2
        top_y = window.height - 120

        self._renderer.draw_title("Game Over", center_x, top_y)
        self._draw_summary_table(center_x=center_x, top_y=window.height - 220)

        if self._phase is GameOverPhase.SUMMARY:
            self._draw_summary_prompt(center_x=center_x)
            return

        if self._phase is GameOverPhase.NAME_ENTRY:
            self._draw_name_entry(center_x=center_x)
            return

        self._draw_options(center_x=center_x)

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle sub-phase progression, name input, and option selection."""
        del modifiers

        if self._phase is GameOverPhase.SUMMARY:
            if self._summary_elapsed_seconds < self._summary_min_seconds:
                return
            if self._is_practice:
                self._phase = GameOverPhase.OPTIONS
            elif self._qualifies_for_leaderboard:
                self._phase = GameOverPhase.NAME_ENTRY
            else:
                self._phase = GameOverPhase.OPTIONS
            return

        if self._phase is GameOverPhase.NAME_ENTRY:
            self._handle_name_entry_key(key)
            return

        self._handle_options_key(key)

    def _check_qualification(self, high_scores: list[HighScoreEntry]) -> bool:
        """Return whether the current score qualifies for top-10 leaderboard."""
        leaderboard_limit = 10
        sorted_scores = sorted(high_scores, key=lambda entry: entry.score, reverse=True)
        if len(sorted_scores) < leaderboard_limit:
            return True
        cutoff = sorted_scores[leaderboard_limit - 1].score
        return self.run_summary.score > cutoff

    def _submit_high_score(self) -> bool:
        """Persist the typed high-score entry when validation succeeds."""
        if self._has_saved_high_score:
            return True
        if len(self._name_buffer) < self._name_min_length:
            return False

        persistence = self._resolve_persistence()
        if persistence is None:
            return False

        settings = persistence.load_settings()
        high_scores = persistence.load_high_scores()
        high_scores.append(
            HighScoreEntry(
                name=self._name_buffer,
                score=self.run_summary.score,
                level_reached=self.run_summary.level_reached,
                difficulty=settings.difficulty,
                enemies_destroyed=self.run_summary.enemies_destroyed,
                currency_collected=self.run_summary.currency_collected,
                currency_spent=self.run_summary.currency_spent,
                date=datetime.now(UTC).isoformat(),
            )
        )
        high_scores.sort(key=lambda entry: entry.score, reverse=True)
        persistence.save_high_scores(high_scores[: GAME_CONFIG.max_high_scores])
        self._has_saved_high_score = True
        return True

    def _handle_name_entry_key(self, key: int) -> None:
        """Process keyboard input for high-score name entry."""
        if key == arcade.key.BACKSPACE:
            self._name_buffer = self._name_buffer[:-1]
            return

        if key == arcade.key.ENTER:
            if self._submit_high_score():
                self._phase = GameOverPhase.OPTIONS
            return

        character = self._key_to_alphanumeric(key)
        if character is None:
            return
        if len(self._name_buffer) >= self._name_max_length:
            return
        self._name_buffer += character

    def _handle_options_key(self, key: int) -> None:
        """Process navigation and selection keys for the options menu."""
        if key in self._up_keys():
            self._selected_option_index = (self._selected_option_index - 1) % len(
                self._options
            )
            return

        if key in self._down_keys():
            self._selected_option_index = (self._selected_option_index + 1) % len(
                self._options
            )
            return

        if key not in self._select_keys():
            return

        if self._selected_option_index == 0:
            if self._is_practice:
                from asterax.app.src.states.practice_config import PracticeConfigState

                self.state_machine.switch_state(PracticeConfigState(self.state_machine))
            else:
                from asterax.app.src.states.game_init import GameInitState

                self.state_machine.switch_state(GameInitState(self.state_machine))
            return

        from asterax.app.src.states.main_menu import MainMenuState

        self.state_machine.switch_state(MainMenuState(self.state_machine))

    def _draw_summary_table(self, center_x: float, top_y: float) -> None:
        """Draw run-summary values as a two-column label/value table."""
        labels = [
            "Final Score",
            "Level Reached",
            "Enemies Destroyed",
            "Asteroids Destroyed",
            "Currency Earned",
            "Currency Spent",
            "Insurance Tier",
        ]
        values = [
            str(self.run_summary.score),
            str(self.run_summary.level_reached),
            str(self.run_summary.enemies_destroyed),
            str(self.run_summary.asteroids_destroyed),
            str(self.run_summary.currency_collected),
            str(self.run_summary.currency_spent),
            self.run_summary.insurance_tier.title(),
        ]

        label_x = center_x - 230
        value_x = center_x + 130
        row_spacing = 40
        for index, (label, value) in enumerate(zip(labels, values, strict=True)):
            y = top_y - (index * row_spacing)
            arcade.draw_text(
                f"{label}:",
                label_x,
                y,
                (190, 210, 225, 255),
                22,
                anchor_x="left",
            )
            arcade.draw_text(
                value,
                value_x,
                y,
                (230, 245, 255, 255),
                22,
                anchor_x="left",
            )

    def _draw_summary_prompt(self, center_x: float) -> None:
        """Render summary-phase prompt and qualification notice."""
        prompt = (
            "Press any key to continue"
            if self._summary_elapsed_seconds >= self._summary_min_seconds
            else "..."
        )
        if self._is_practice:
            qualification_text = "Practice Mode -- Score not recorded"
        else:
            qualification_text = (
                "Score qualifies for leaderboard!"
                if self._qualifies_for_leaderboard
                else "Score does not qualify for leaderboard"
            )
        arcade.draw_text(
            qualification_text,
            center_x,
            170,
            (
                (255, 220, 80, 255)
                if self._qualifies_for_leaderboard or self._is_practice
                else (190, 210, 225, 255)
            ),
            22,
            anchor_x="center",
        )
        arcade.draw_text(
            prompt,
            center_x,
            120,
            (200, 220, 240, 255),
            20,
            anchor_x="center",
        )

    def _draw_name_entry(self, center_x: float) -> None:
        """Render high-score name-entry UI with a blinking cursor."""
        cursor = "_" if self._cursor_visible else " "
        padded_value = self._name_buffer
        if len(padded_value) < self._name_max_length:
            padded_value += cursor
        arcade.draw_text(
            "New High Score! Enter your name (3-10, A-Z 0-9)",
            center_x,
            170,
            (255, 220, 80, 255),
            20,
            anchor_x="center",
        )
        arcade.draw_text(
            padded_value,
            center_x,
            130,
            (230, 245, 255, 255),
            30,
            anchor_x="center",
        )
        arcade.draw_text(
            "Backspace deletes • Enter confirms",
            center_x,
            95,
            (190, 210, 225, 255),
            18,
            anchor_x="center",
        )

    def _draw_options(self, center_x: float) -> None:
        """Render the post-game options menu."""
        self._renderer.draw_menu_options(
            options=self._options,
            selected=self._selected_option_index,
            x=center_x,
            y=160,
            spacing=52.0,
        )

    def _key_to_alphanumeric(self, key: int) -> str | None:
        """Convert supported key constants to uppercase alphanumeric characters."""
        if arcade.key.A <= key <= arcade.key.Z:
            return chr(key).upper()

        if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
            index = key - arcade.key.KEY_0
            return str(index)

        numpad_zero = getattr(arcade.key, "NUM_0", None)
        numpad_nine = getattr(arcade.key, "NUM_9", None)
        if (
            isinstance(numpad_zero, int)
            and isinstance(numpad_nine, int)
            and numpad_zero <= key <= numpad_nine
        ):
            index = key - numpad_zero
            return str(index)

        return None

    def _up_keys(self) -> set[int]:
        """Return keys accepted for upward option navigation."""
        keys = {arcade.key.UP, arcade.key.W}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("thrust"))
        return keys

    def _down_keys(self) -> set[int]:
        """Return keys accepted for downward option navigation."""
        keys = {arcade.key.DOWN, arcade.key.S}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("brake"))
        return keys

    def _select_keys(self) -> set[int]:
        """Return keys accepted for selecting the current option."""
        keys = {arcade.key.ENTER, arcade.key.SPACE}
        input_manager = self._input_manager()
        if input_manager is not None:
            keys.add(input_manager.get_binding("fire"))
        return keys

    def _input_manager(self) -> InputManager | None:
        """Return the active input manager when available on the window."""
        window = arcade.get_window()
        input_manager = getattr(window, "input_manager", None)
        if isinstance(input_manager, InputManager):
            return input_manager
        return None

    def _play_sound(self, sound_name: str) -> None:
        """Play a sound when an audio manager is available on the window."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        audio_manager = getattr(window, "audio_manager", None)
        if audio_manager is not None:
            audio_manager.play(sound_name)
