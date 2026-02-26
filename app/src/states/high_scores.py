"""High scores leaderboard state."""

from __future__ import annotations

from typing import Final

import arcade
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.persistence_manager import PersistenceManager
from asterax.app.src.persistence.schemas import HighScoreEntry
from asterax.app.src.rendering.menu_renderer import MenuRenderer
from asterax.app.src.states.base_state import BaseState

_MAX_VISIBLE_ENTRIES: Final[int] = 10
_FILTER_ORDER: Final[tuple[str, ...]] = ("all", "casual", "classic", "hard")


class HighScoresState(BaseState):
    """Persistent local leaderboard with optional difficulty filtering."""

    NO_SCORES_MESSAGE: Final[str] = "No scores yet -- start a new game!"

    def __init__(self, state_machine) -> None:
        """Initialize leaderboard rendering and filter state.

        Args:
            state_machine: Owning state machine instance.
        """
        super().__init__(state_machine)
        self._renderer = MenuRenderer()
        self._scores: list[HighScoreEntry] = []
        self._current_filter: str = "all"
        self._filter_enabled: bool = False

    def on_enter(self) -> None:
        """Load scores and initialize filter availability."""
        self._scores = self._load_scores()
        unique_difficulties = {
            entry.difficulty.lower() for entry in self._scores if entry.difficulty
        }
        self._filter_enabled = len(unique_difficulties) > 1
        if not self._filter_enabled:
            self._current_filter = "all"

    def on_draw(self) -> None:
        """Render leaderboard rows or an empty-state message."""
        window = arcade.get_window()
        center_x = window.width / 2
        self._renderer.draw_title("High Scores", center_x, window.height - 80)

        if self._filter_enabled:
            arcade.draw_text(
                f"Showing: {self._current_filter.title()}  [Left/Right: Filter]",
                center_x,
                window.height - 136,
                (170, 190, 210, 255),
                18,
                anchor_x="center",
            )

        filtered_scores = self._filtered_scores()[:_MAX_VISIBLE_ENTRIES]
        if not filtered_scores:
            arcade.draw_text(
                self.NO_SCORES_MESSAGE,
                center_x,
                window.height / 2,
                (210, 226, 240, 255),
                26,
                anchor_x="center",
                anchor_y="center",
            )
        else:
            self._draw_table(filtered_scores)

        arcade.draw_text(
            "ESC/Backspace: Back",
            center_x,
            24,
            (170, 190, 210, 255),
            18,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle filter cycling and return-to-menu shortcuts.

        Args:
            key: Arcade key constant that was pressed.
            modifiers: Key modifier bitmask.
        """
        del modifiers

        from asterax.app.src.states.main_menu import MainMenuState

        if key in {arcade.key.ESCAPE, arcade.key.BACKSPACE, self._pause_key()}:
            self.state_machine.switch_state(MainMenuState(self.state_machine))
            return

        if not self._filter_enabled:
            return

        if key in {arcade.key.LEFT, arcade.key.A}:
            self._cycle_filter(-1)
            return

        if key in {arcade.key.RIGHT, arcade.key.D}:
            self._cycle_filter(1)

    def _load_scores(self) -> list[HighScoreEntry]:
        """Load and sort scores by descending score.

        Returns:
            Sorted leaderboard entries.
        """
        window = arcade.get_window()
        persistence = getattr(window, "persistence", None)
        if not hasattr(persistence, "load_high_scores"):
            persistence = PersistenceManager()

        entries = persistence.load_high_scores()
        return sorted(entries, key=lambda entry: entry.score, reverse=True)

    def _cycle_filter(self, direction: int) -> None:
        """Cycle the active difficulty filter.

        Args:
            direction: -1 for previous, +1 for next.
        """
        current_index = _FILTER_ORDER.index(self._current_filter)
        next_index = (current_index + direction) % len(_FILTER_ORDER)
        self._current_filter = _FILTER_ORDER[next_index]

    def _filtered_scores(self) -> list[HighScoreEntry]:
        """Return entries constrained by the active difficulty filter."""
        if self._current_filter == "all":
            return self._scores

        return [
            entry
            for entry in self._scores
            if entry.difficulty.lower() == self._current_filter
        ]

    def _draw_table(self, entries: list[HighScoreEntry]) -> None:
        """Draw leaderboard entries in fixed columns.

        Args:
            entries: Already-filtered leaderboard entries.
        """
        window = arcade.get_window()
        left_x = window.width * 0.12
        y = window.height - 200

        headers = ["#", "Name", "Score", "Level", "Difficulty", "Date"]
        columns = [
            left_x,
            left_x + 70,
            left_x + 230,
            left_x + 390,
            left_x + 500,
            left_x + 650,
        ]

        for header, x in zip(headers, columns, strict=True):
            arcade.draw_text(
                header,
                x,
                y,
                (255, 220, 80, 255),
                20,
                anchor_x="left",
            )

        y -= 40
        for rank, entry in enumerate(entries, start=1):
            date_display = (
                entry.date.split("T", maxsplit=1)[0]
                if "T" in entry.date
                else entry.date
            )
            row = [
                str(rank),
                entry.name,
                str(entry.score),
                str(entry.level_reached),
                entry.difficulty.title(),
                date_display,
            ]
            for value, x in zip(row, columns, strict=True):
                arcade.draw_text(
                    value,
                    x,
                    y,
                    (210, 226, 240, 255),
                    20,
                    anchor_x="left",
                )
            y -= 34

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
