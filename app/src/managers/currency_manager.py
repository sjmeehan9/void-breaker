"""Currency accumulation and spending manager.

This module is the single authority for all currency transactions during a run.
All earn, spend, and deduct operations flow through ``CurrencyManager``; no
other module should write to ``GameState.currency`` directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asterax.app.src.config.game_config import GameState


@dataclass(slots=True)
class CurrencyRunStats:
    """Cumulative currency statistics for the current run.

    Attributes:
        total_earned: Sum of all currency earned (pickups) this run.
        total_spent: Sum of all currency spent (purchases + insurance) this run.
    """

    total_earned: int
    total_spent: int


class CurrencyManager:
    """Central authority for all currency transactions in a run.

    When a ``GameState`` is provided the manager reads and writes
    ``game_state.currency`` as its backing store, keeping it in sync
    at all times.  When no ``GameState`` is provided (e.g. unit tests)
    the manager maintains its own internal balance.

    Args:
        game_state: Optional game-state whose ``currency`` field this
            manager should own.  When supplied, all balance reads/writes
            go through ``game_state.currency``.
    """

    def __init__(self, game_state: GameState | None = None) -> None:
        """Initialize an empty run currency ledger.

        Args:
            game_state: Optional game-state to use as the backing store
                for the currency balance.
        """
        self._game_state = game_state
        self._balance: int = 0  # used only when game_state is None
        self.total_earned: int = 0
        self.total_spent: int = 0

    # ------------------------------------------------------------------
    # Internal backing-store helpers
    # ------------------------------------------------------------------

    def _get_balance(self) -> int:
        if self._game_state is not None:
            return self._game_state.currency
        return self._balance

    def _set_balance(self, value: int) -> None:
        if self._game_state is not None:
            self._game_state.currency = value
        else:
            self._balance = value

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def earn(self, amount: int) -> None:
        """Increase currency balance by *amount*.

        Args:
            amount: Positive integer to add.

        Raises:
            ValueError: If *amount* is zero or negative.
        """
        if amount <= 0:
            raise ValueError(f"amount must be a positive integer, got {amount!r}")
        self._set_balance(self._get_balance() + amount)
        self.total_earned += amount

    def spend(self, amount: int) -> bool:
        """Spend *amount* of currency if the balance is sufficient.

        Args:
            amount: Positive integer to deduct.

        Returns:
            ``True`` if the spend succeeded; ``False`` if the balance was
            insufficient (state is unchanged in that case).

        Raises:
            ValueError: If *amount* is zero or negative.
        """
        if amount <= 0:
            raise ValueError(f"amount must be a positive integer, got {amount!r}")
        if self._get_balance() < amount:
            return False
        self._set_balance(self._get_balance() - amount)
        self.total_spent += amount
        return True

    def can_spend(self, amount: int) -> bool:
        """Return whether *amount* can be spent without modifying state.

        Args:
            amount: Positive integer to check.

        Returns:
            ``True`` if the current balance is at least *amount*.

        Raises:
            ValueError: If *amount* is zero or negative.
        """
        if amount <= 0:
            raise ValueError(f"amount must be a positive integer, got {amount!r}")
        return self._get_balance() >= amount

    def deduct(self, amount: int) -> bool:
        """Deduct *amount* from the balance (insurance-tier semantic alias).

        Behaves identically to :meth:`spend` but signals an insurance
        deduction at the call site for clarity.

        Args:
            amount: Positive integer to deduct.

        Returns:
            ``True`` if the deduction succeeded; ``False`` otherwise.

        Raises:
            ValueError: If *amount* is zero or negative.
        """
        return self.spend(amount)

    def get_balance(self) -> int:
        """Return the current available currency balance.

        Returns:
            Current balance as a non-negative integer.
        """
        return self._get_balance()

    def get_run_stats(self) -> CurrencyRunStats:
        """Return cumulative currency statistics for the current run.

        Returns:
            A :class:`CurrencyRunStats` snapshot with ``total_earned`` and
            ``total_spent`` counters.
        """
        return CurrencyRunStats(
            total_earned=self.total_earned,
            total_spent=self.total_spent,
        )

    def reset(self) -> None:
        """Reset balance and aggregate counters for a new run."""
        self._set_balance(0)
        self.total_earned = 0
        self.total_spent = 0
