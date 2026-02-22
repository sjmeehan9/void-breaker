"""Tests for state stack transitions and delegation."""

from asterax.app.src.states.base_state import BaseState
from asterax.app.src.states.state_machine import StateMachine


class RecordingState(BaseState):
    """State used to record lifecycle/delegation activity in tests."""

    def __init__(
        self, state_machine: StateMachine, name: str, calls: list[str]
    ) -> None:
        super().__init__(state_machine)
        self.name = name
        self.calls = calls

    def on_enter(self) -> None:
        self.calls.append(f"{self.name}:enter")

    def on_exit(self) -> None:
        self.calls.append(f"{self.name}:exit")

    def on_update(self, delta_time: float) -> None:
        self.calls.append(f"{self.name}:update:{delta_time}")

    def on_draw(self) -> None:
        self.calls.append(f"{self.name}:draw")

    def on_key_press(self, key: int, modifiers: int) -> None:
        self.calls.append(f"{self.name}:press:{key}:{modifiers}")

    def on_key_release(self, key: int, modifiers: int) -> None:
        self.calls.append(f"{self.name}:release:{key}:{modifiers}")


def test_switch_state_calls_exit_then_enter() -> None:
    """switch_state should exit the previous state before entering the new one."""
    machine = StateMachine()
    calls: list[str] = []

    first = RecordingState(machine, "first", calls)
    second = RecordingState(machine, "second", calls)

    machine.switch_state(first)
    calls.clear()
    machine.switch_state(second)

    assert calls == ["first:exit", "second:enter"]
    assert machine.current_state is second


def test_push_pop_preserves_underlying_state() -> None:
    """push_state/pop_state should pause and resume the underlying state."""
    machine = StateMachine()
    calls: list[str] = []

    base = RecordingState(machine, "base", calls)
    overlay = RecordingState(machine, "overlay", calls)

    machine.switch_state(base)
    calls.clear()
    machine.push_state(overlay)
    machine.pop_state()

    assert calls == ["base:exit", "overlay:enter", "overlay:exit", "base:enter"]
    assert machine.current_state is base


def test_draw_update_and_input_delegate_to_expected_states() -> None:
    """draw should iterate bottom-to-top; update/input should hit only top state."""
    machine = StateMachine()
    calls: list[str] = []

    bottom = RecordingState(machine, "bottom", calls)
    top = RecordingState(machine, "top", calls)

    machine.switch_state(bottom)
    machine.push_state(top)
    calls.clear()

    machine.draw()
    machine.update(0.5)
    machine.on_key_press(1, 2)
    machine.on_key_release(3, 4)

    assert calls == [
        "bottom:draw",
        "top:draw",
        "top:update:0.5",
        "top:press:1:2",
        "top:release:3:4",
    ]


def test_empty_stack_operations_are_no_ops() -> None:
    """State machine operations should not raise when no states are present."""
    machine = StateMachine()

    machine.pop_state()
    machine.update(0.1)
    machine.draw()
    machine.on_key_press(1, 0)
    machine.on_key_release(1, 0)

    assert machine.current_state is None
