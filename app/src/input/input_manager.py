"""Input manager for keyboard event handling and configurable key bindings."""

from __future__ import annotations

import logging

import arcade
from asterax.app.src.persistence.schemas import GameSettings

logger = logging.getLogger(__name__)

# Mapping from human-readable string key names to arcade.key constants
KEY_NAME_MAP: dict[str, int] = {
    # Arrow keys
    "LEFT": arcade.key.LEFT,
    "RIGHT": arcade.key.RIGHT,
    "UP": arcade.key.UP,
    "DOWN": arcade.key.DOWN,
    # Special keys
    "SPACE": arcade.key.SPACE,
    "LSHIFT": arcade.key.LSHIFT,
    "RSHIFT": arcade.key.RSHIFT,
    "ESCAPE": arcade.key.ESCAPE,
    "ENTER": arcade.key.ENTER,
    "BACKSPACE": arcade.key.BACKSPACE,
    "TAB": arcade.key.TAB,
    # Letter keys A-Z
    "A": arcade.key.A,
    "B": arcade.key.B,
    "C": arcade.key.C,
    "D": arcade.key.D,
    "E": arcade.key.E,
    "F": arcade.key.F,
    "G": arcade.key.G,
    "H": arcade.key.H,
    "I": arcade.key.I,
    "J": arcade.key.J,
    "K": arcade.key.K,
    "L": arcade.key.L,
    "M": arcade.key.M,
    "N": arcade.key.N,
    "O": arcade.key.O,
    "P": arcade.key.P,
    "Q": arcade.key.Q,
    "R": arcade.key.R,
    "S": arcade.key.S,
    "T": arcade.key.T,
    "U": arcade.key.U,
    "V": arcade.key.V,
    "W": arcade.key.W,
    "X": arcade.key.X,
    "Y": arcade.key.Y,
    "Z": arcade.key.Z,
    # Number keys
    "KEY_0": arcade.key.KEY_0,
    "KEY_1": arcade.key.KEY_1,
    "KEY_2": arcade.key.KEY_2,
    "KEY_3": arcade.key.KEY_3,
    "KEY_4": arcade.key.KEY_4,
    "KEY_5": arcade.key.KEY_5,
    "KEY_6": arcade.key.KEY_6,
    "KEY_7": arcade.key.KEY_7,
    "KEY_8": arcade.key.KEY_8,
    "KEY_9": arcade.key.KEY_9,
}

# Default key bindings matching solution-design.md
DEFAULT_BINDINGS: dict[str, str] = {
    "rotate_left": "LEFT",
    "rotate_right": "RIGHT",
    "thrust": "UP",
    "fire": "SPACE",
    "brake": "DOWN",
    "special": "LSHIFT",
    "pause": "ESCAPE",
}


class InputManager:
    """Manages keyboard input state and configurable key bindings.

    The InputManager maintains a set of currently-held keys and translates
    string key names (from settings JSON) to Arcade integer key constants.
    States can query is_action_held() for continuous actions like thrust/rotation,
    and receive discrete key events via the state machine for one-shot actions.
    """

    def __init__(self, settings: GameSettings) -> None:
        """Initialize the input manager with key bindings from settings.

        Args:
            settings: GameSettings containing key binding configuration
        """
        self.keys_held: set[int] = set()
        self._bindings: dict[str, int] = {}
        self._build_bindings(settings)

    def _build_bindings(self, settings: GameSettings) -> None:
        """Build the bindings dictionary from settings.

        If a key name from settings is not found in KEY_NAME_MAP, logs a warning
        and uses the default binding for that action.

        Args:
            settings: GameSettings containing key binding configuration
        """
        action_to_setting_key = {
            "rotate_left": settings.key_rotate_left,
            "rotate_right": settings.key_rotate_right,
            "thrust": settings.key_thrust,
            "fire": settings.key_fire,
            "brake": settings.key_brake,
            "special": settings.key_special,
            "pause": settings.key_pause,
        }

        for action, key_name in action_to_setting_key.items():
            if key_name in KEY_NAME_MAP:
                self._bindings[action] = KEY_NAME_MAP[key_name]
            else:
                logger.warning(
                    f"Invalid key name '{key_name}' for action '{action}', "
                    f"falling back to default '{DEFAULT_BINDINGS[action]}'"
                )
                self._bindings[action] = KEY_NAME_MAP[DEFAULT_BINDINGS[action]]

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle key press event by adding key to the held set.

        Args:
            key: Arcade key constant
            modifiers: Keyboard modifiers (shift, ctrl, etc.)
        """
        self.keys_held.add(key)

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Handle key release event by removing key from the held set.

        Args:
            key: Arcade key constant
            modifiers: Keyboard modifiers (shift, ctrl, etc.)
        """
        self.keys_held.discard(key)

    def is_action_held(self, action: str) -> bool:
        """Check if the key bound to a named action is currently held.

        Args:
            action: Action name (e.g., "thrust", "rotate_left", "fire")

        Returns:
            True if the bound key is currently held, False otherwise
        """
        return self._bindings.get(action, -1) in self.keys_held

    def get_binding(self, action: str) -> int:
        """Get the Arcade key constant bound to a named action.

        Args:
            action: Action name (e.g., "thrust", "rotate_left", "fire")

        Returns:
            Arcade key constant for the bound key, or -1 if action not found
        """
        return self._bindings.get(action, -1)

    def update_bindings(self, settings: GameSettings) -> None:
        """Refresh key bindings from new settings without restart.

        This method is used when the player remaps keys in the Settings screen.

        Args:
            settings: Updated GameSettings with new key bindings
        """
        self._bindings.clear()
        self._build_bindings(settings)
