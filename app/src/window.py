"""Arcade window implementation for VoidBreaker."""

from pathlib import Path
from typing import Final

import arcade
from asterax.app.src.audio.audio_manager import AudioManager
from asterax.app.src.config.game_config import GAME_CONFIG
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.persistence_manager import PersistenceManager
from asterax.app.src.rendering.hud import HUDRenderer
from asterax.app.src.rendering.starfield import StarfieldRenderer
from asterax.app.src.rendering.transitions import ScreenShake
from asterax.app.src.states.main_menu import MainMenuState
from asterax.app.src.states.state_machine import StateMachine

PHYSICS_DT: Final[float] = 1.0 / 60.0
MAX_FRAME_TIME: Final[float] = 0.25


class VoidBreakerWindow(arcade.Window):
    """Main Arcade window with a fixed-timestep update loop."""

    def __init__(
        self,
        width: int = GAME_CONFIG.window_width,
        height: int = GAME_CONFIG.window_height,
        title: str = GAME_CONFIG.window_title,
    ) -> None:
        """Initialize the game window and fixed-step timing state."""
        super().__init__(width=width, height=height, title=title, resizable=False)
        self.accumulator: float = 0.0

        self.persistence = PersistenceManager()
        settings = self.persistence.load_settings()
        self.runtime_settings = settings
        self.input_manager = InputManager(settings)
        sound_dir = Path(__file__).resolve().parents[2] / "assets" / "sounds"
        self.audio_manager = AudioManager(settings, sound_dir)
        self.starfield = StarfieldRenderer(width=width, height=height)
        self.hud_renderer = HUDRenderer(window_width=width, window_height=height)
        self.screen_shake = ScreenShake()
        self._game_camera: arcade.Camera2D | None = None
        if hasattr(self, "ctx"):
            self._game_camera = arcade.Camera2D(window=self)

        self.state_machine = StateMachine()
        self.state_machine.switch_state(MainMenuState(self.state_machine))
        self.set_update_rate(PHYSICS_DT)

    def on_update(self, delta_time: float) -> None:
        """Advance simulation using a fixed timestep accumulator."""
        frame_time = min(delta_time, MAX_FRAME_TIME)
        if hasattr(self, "screen_shake"):
            self.screen_shake.update(frame_time)
        self.accumulator += frame_time

        while self.accumulator >= PHYSICS_DT:
            self._physics_step(PHYSICS_DT)
            self.accumulator -= PHYSICS_DT

    def _physics_step(self, dt: float) -> None:
        """Advance one fixed-duration physics tick."""
        self.state_machine.update(dt)

    def on_draw(self) -> None:
        """Render a cleared black frame."""
        self.clear()
        camera = getattr(self, "_game_camera", None)
        if camera is None and hasattr(self, "ctx"):
            camera = arcade.Camera2D(window=self)
            self._game_camera = camera

        offset_x = 0.0
        offset_y = 0.0
        if hasattr(self, "screen_shake"):
            offset_x, offset_y = self.screen_shake.get_offset()

        if camera is not None:
            camera.equalise()
            camera.position = (offset_x, offset_y)
            camera.use()

        self.starfield.draw()
        self.state_machine.draw()

        if camera is not None:
            camera.equalise()
            camera.position = (0.0, 0.0)
            camera.use()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle key press events."""
        self.input_manager.on_key_press(key, modifiers)
        self.state_machine.on_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Handle key release events."""
        self.input_manager.on_key_release(key, modifiers)
        self.state_machine.on_key_release(key, modifiers)

    def trigger_screen_shake(self, intensity: str) -> None:
        """Trigger screen shake with the provided intensity setting."""
        self.screen_shake.trigger(intensity)

    def update_runtime_settings(self, settings: object) -> None:
        """Update runtime settings cache for systems that read per-frame options."""
        self.runtime_settings = settings
