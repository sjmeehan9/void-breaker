"""State protocol and base class for game states."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from asterax.app.src.states.state_machine import StateMachine


class GameState(Protocol):
    """Protocol implemented by all game states."""

    def on_enter(self) -> None:
        """Run logic when the state becomes active."""

    def on_exit(self) -> None:
        """Run logic when the state is deactivated."""

    def on_update(self, delta_time: float) -> None:
        """Advance state logic for a frame."""

    def on_draw(self) -> None:
        """Render state visuals."""

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle a key press event."""

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Handle a key release event."""


class BaseState(ABC):
    """Abstract base state with no-op lifecycle hooks."""

    def __init__(self, state_machine: StateMachine) -> None:
        """Store a reference to the owning state machine."""
        self.state_machine = state_machine

    def on_enter(self) -> None:
        """Run logic when the state becomes active."""

    def on_exit(self) -> None:
        """Run logic when the state is deactivated."""

    def on_update(self, delta_time: float) -> None:
        """Advance state logic for a frame."""

    def on_draw(self) -> None:
        """Render state visuals."""

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle a key press event."""

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Handle a key release event."""
