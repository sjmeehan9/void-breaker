"""State stack manager for the game window."""

from __future__ import annotations

from asterax.app.src.states.base_state import GameState


class StateMachine:
    """Manages active game states and transitions."""

    def __init__(self) -> None:
        """Initialize an empty state stack."""
        self._stack: list[GameState] = []

    @property
    def current_state(self) -> GameState | None:
        """Return the current top-most state, if any."""
        return self._stack[-1] if self._stack else None

    def switch_state(self, state: GameState) -> None:
        """Replace the current state stack with a new state."""
        if self._stack:
            self._stack[-1].on_exit()
        self._stack.clear()
        self._stack.append(state)
        state.on_enter()

    def push_state(self, state: GameState) -> None:
        """Push an overlay state on top of the active state."""
        self._stack.append(state)
        state.on_enter()

    def pop_state(self) -> None:
        """Pop the top state and reactivate the previous state if present."""
        if not self._stack:
            return
        popped_state = self._stack.pop()
        popped_state.on_exit()

    def update(self, delta_time: float) -> None:
        """Update only the active top-most state."""
        if self._stack:
            self._stack[-1].on_update(delta_time)

    def draw(self) -> None:
        """Draw states bottom-to-top to support overlays."""
        for state in self._stack:
            state.on_draw()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Route key press events to the active top state."""
        if self._stack:
            self._stack[-1].on_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Route key release events to the active top state."""
        if self._stack:
            self._stack[-1].on_key_release(key, modifiers)
