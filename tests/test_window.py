"""Tests for fixed timestep behaviour in the game window."""

import asterax.app.src.window as window_module
import pytest
from asterax.app.src.window import MAX_FRAME_TIME, PHYSICS_DT, VoidBreakerWindow


def test_on_update_uses_fixed_timestep() -> None:
    """on_update should execute physics steps based on fixed dt increments."""
    window = object.__new__(VoidBreakerWindow)
    window.accumulator = 0.0

    steps: list[float] = []

    def record_step(dt: float) -> None:
        steps.append(dt)

    window._physics_step = record_step  # type: ignore[method-assign]
    window.on_update(PHYSICS_DT * 2.5)

    assert len(steps) == 2
    assert all(step == PHYSICS_DT for step in steps)
    assert window.accumulator == pytest.approx(PHYSICS_DT * 0.5)


def test_on_update_caps_large_delta_time() -> None:
    """on_update should cap frame time to avoid spiral-of-death behaviour."""
    window = object.__new__(VoidBreakerWindow)
    window.accumulator = 0.0

    steps: list[float] = []

    def record_step(dt: float) -> None:
        steps.append(dt)

    window._physics_step = record_step  # type: ignore[method-assign]
    window.on_update(MAX_FRAME_TIME * 2)

    assert len(steps) == int(MAX_FRAME_TIME / PHYSICS_DT)


def test_window_initializes_state_machine_and_main_menu(monkeypatch) -> None:
    """Window init should create state machine and switch to MainMenuState."""
    call_order: list[str] = []

    def fake_window_init(
        self: VoidBreakerWindow,
        width: int,
        height: int,
        title: str,
        resizable: bool,
    ) -> None:
        del width, height, title, resizable
        call_order.append("window_init")

    class FakePersistenceManager:
        def __init__(self, base_dir=None):
            del base_dir
            call_order.append("persistence_init")

        def load_settings(self):
            from asterax.app.src.persistence.schemas import GameSettings

            call_order.append("load_settings")
            return GameSettings()

    class FakeInputManager:
        def __init__(self, settings):
            del settings
            call_order.append("input_init")

    class FakeAudioManager:
        def __init__(self, settings, sound_dir):
            del settings, sound_dir
            call_order.append("audio_init")

    class FakeStarfieldRenderer:
        def __init__(self, width: int, height: int):
            del width, height
            call_order.append("starfield_init")

    class FakeHUDRenderer:
        def __init__(self, window_width: int, window_height: int):
            del window_width, window_height
            call_order.append("hud_init")

    class FakeStateMachine:
        def __init__(self) -> None:
            call_order.append("machine_init")

        def switch_state(self, state: object) -> None:
            del state
            call_order.append("switch_state")

    class FakeMainMenuState:
        def __init__(self, state_machine: FakeStateMachine) -> None:
            del state_machine
            call_order.append("main_menu_init")

    monkeypatch.setattr(window_module.arcade.Window, "__init__", fake_window_init)
    monkeypatch.setattr(window_module, "PersistenceManager", FakePersistenceManager)
    monkeypatch.setattr(window_module, "InputManager", FakeInputManager)
    monkeypatch.setattr(window_module, "AudioManager", FakeAudioManager)
    monkeypatch.setattr(window_module, "StarfieldRenderer", FakeStarfieldRenderer)
    monkeypatch.setattr(window_module, "HUDRenderer", FakeHUDRenderer)
    monkeypatch.setattr(window_module, "StateMachine", FakeStateMachine)
    monkeypatch.setattr(window_module, "MainMenuState", FakeMainMenuState)
    monkeypatch.setattr(
        window_module.VoidBreakerWindow,
        "set_update_rate",
        lambda self, rate: call_order.append(f"set_rate:{rate}"),
    )

    window_module.VoidBreakerWindow()

    assert call_order == [
        "window_init",
        "persistence_init",
        "load_settings",
        "input_init",
        "audio_init",
        "starfield_init",
        "hud_init",
        "machine_init",
        "main_menu_init",
        "switch_state",
        f"set_rate:{PHYSICS_DT}",
    ]


def test_window_delegates_draw_update_and_input_to_state_machine() -> None:
    """Window should delegate simulation and input methods to state machine."""
    window = object.__new__(VoidBreakerWindow)
    calls: list[str] = []

    class FakeInputManager:
        def on_key_press(self, key: int, modifiers: int) -> None:
            calls.append(f"input_press:{key}:{modifiers}")

        def on_key_release(self, key: int, modifiers: int) -> None:
            calls.append(f"input_release:{key}:{modifiers}")

    class FakeStateMachine:
        def update(self, dt: float) -> None:
            calls.append(f"update:{dt}")

        def draw(self) -> None:
            calls.append("draw")

        def on_key_press(self, key: int, modifiers: int) -> None:
            calls.append(f"press:{key}:{modifiers}")

        def on_key_release(self, key: int, modifiers: int) -> None:
            calls.append(f"release:{key}:{modifiers}")

    class FakeStarfield:
        def draw(self) -> None:
            calls.append("starfield")

    window.input_manager = FakeInputManager()  # type: ignore[assignment]
    window.starfield = FakeStarfield()  # type: ignore[assignment]
    window.state_machine = FakeStateMachine()  # type: ignore[assignment]
    window.clear = lambda: calls.append("clear")

    window._physics_step(PHYSICS_DT)
    window.on_draw()
    window.on_key_press(10, 20)
    window.on_key_release(30, 40)

    assert calls == [
        f"update:{PHYSICS_DT}",
        "clear",
        "starfield",
        "draw",
        "input_press:10:20",
        "press:10:20",
        "input_release:30:40",
        "release:30:40",
    ]
