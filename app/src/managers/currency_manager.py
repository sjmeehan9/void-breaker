"""Currency accumulation and spending manager."""

from __future__ import annotations


class CurrencyManager:
    """Track run currency balance and aggregate totals."""

    def __init__(self) -> None:
        """Initialize an empty run currency ledger."""
        self._balance = 0
        self.total_earned = 0
        self.total_spent = 0

    def earn(self, amount: int) -> None:
        """Increase currency balance by a non-negative amount."""
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self._balance += amount
        self.total_earned += amount

    def spend(self, amount: int) -> bool:
        """Spend currency if affordable and report whether it succeeded."""
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if amount > self._balance:
            return False
        self._balance -= amount
        self.total_spent += amount
        return True

    def get_balance(self) -> int:
        """Return the current available currency balance."""
        return self._balance

    def reset(self) -> None:
        """Reset balance and aggregate counters for a new run."""
        self._balance = 0
        self.total_earned = 0
        self.total_spent = 0
