"""Functional game-over state with run summary and high-score persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import arcade
from asterax.app.src.config.game_config import GAME_CONFIG
from asterax.app.src.persistence.schemas import HighScoreEntry
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


class GameOverState(BaseState):
    """Game-over screen that can save qualifying high scores."""

    def __init__(
        self,
        state_machine: StateMachine,
        run_stats: dict[str, int] | None = None,
        persistence: PersistenceManager | None = None,
    ) -> None:
        """Store run stats payload and optional persistence override."""
        super().__init__(state_machine)
        self.run_summary = RunSummary()
        self.is_high_score = False
        self._run_stats_payload = run_stats or {}
        self._persistence = persistence

    def on_enter(self) -> None:
        """Hydrate run summary values and persist high score when qualified."""
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
        )
        persistence = self._resolve_persistence()
        if persistence is None:
            return
        high_scores = persistence.load_high_scores()
        self.is_high_score = len(high_scores) < GAME_CONFIG.max_high_scores or (
            bool(high_scores)
            and self.run_summary.score > min(entry.score for entry in high_scores)
        )
        if not self.is_high_score:
            return
        high_scores.append(
            HighScoreEntry(
                name="AAA",
                score=self.run_summary.score,
                level_reached=self.run_summary.level_reached,
                difficulty="classic",
                enemies_destroyed=self.run_summary.enemies_destroyed,
                currency_collected=self.run_summary.currency_collected,
                currency_spent=self.run_summary.currency_spent,
                date=datetime.now(UTC).date().isoformat(),
            )
        )
        high_scores.sort(key=lambda entry: entry.score, reverse=True)
        persistence.save_high_scores(high_scores[: GAME_CONFIG.max_high_scores])

    def _resolve_persistence(self) -> PersistenceManager | None:
        """Return explicit or window-backed persistence manager when available."""
        if self._persistence is not None:
            return self._persistence
        window = arcade.get_window()
        if window is None:
            return None
        return getattr(window, "persistence", None)

    def on_draw(self) -> None:
        """Render game-over summary and high-score prompt text."""
        window = arcade.get_window()
        arcade.draw_text(
            (
                "GAME OVER\n\n"
                f"Score: {self.run_summary.score}\n"
                f"Level Reached: {self.run_summary.level_reached}\n"
                f"Currency Collected: {self.run_summary.currency_collected}\n"
                f"Currency Spent: {self.run_summary.currency_spent}\n"
                f"Credits Remaining: {self.run_summary.currency_balance}\n\n"
                + (
                    "NEW HIGH SCORE! Initials auto-saved as AAA.\n"
                    if self.is_high_score
                    else ""
                )
                + "Press any key to return to Main Menu"
            ),
            window.width / 2,
            window.height / 2,
            arcade.color.WHITE,
            26,
            anchor_x="center",
            multiline=True,
            width=700,
            align="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Return to main menu from game over on any key press."""
        del modifiers
        del key

        from asterax.app.src.states.main_menu import MainMenuState

        self.state_machine.switch_state(MainMenuState(self.state_machine))
