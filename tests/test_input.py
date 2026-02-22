"""Tests for input manager keyboard event handling and key bindings."""

import arcade
from asterax.app.src.input.input_manager import KEY_NAME_MAP, InputManager
from asterax.app.src.persistence.schemas import GameSettings


def test_on_key_press_and_release_track_keys_held() -> None:
    """Press/release handlers should update keys_held accurately."""
    manager = InputManager(GameSettings())
    manager.on_key_press(arcade.key.SPACE, 0)
    manager.on_key_press(arcade.key.LEFT, 0)

    assert manager.keys_held == {arcade.key.SPACE, arcade.key.LEFT}

    manager.on_key_release(arcade.key.SPACE, 0)
    manager.on_key_release(arcade.key.ENTER, 0)
    assert manager.keys_held == {arcade.key.LEFT}


def test_is_action_held_reflects_bound_key_state() -> None:
    """is_action_held should return True only when the action key is held."""
    manager = InputManager(GameSettings())
    assert manager.is_action_held("fire") is False

    manager.on_key_press(arcade.key.SPACE, 0)
    assert manager.is_action_held("fire") is True


def test_get_binding_uses_default_bindings() -> None:
    """get_binding should resolve expected key codes for default actions."""
    manager = InputManager(GameSettings())

    assert manager.get_binding("rotate_left") == arcade.key.LEFT
    assert manager.get_binding("rotate_right") == arcade.key.RIGHT
    assert manager.get_binding("thrust") == arcade.key.UP
    assert manager.get_binding("fire") == arcade.key.SPACE
    assert manager.get_binding("brake") == arcade.key.DOWN
    assert manager.get_binding("special") == arcade.key.LSHIFT
    assert manager.get_binding("pause") == arcade.key.ESCAPE


def test_update_bindings_changes_active_bindings() -> None:
    """update_bindings should apply new key names from settings."""
    manager = InputManager(GameSettings())
    assert manager.get_binding("fire") == arcade.key.SPACE

    manager.update_bindings(GameSettings(key_fire="RSHIFT"))
    assert manager.get_binding("fire") == arcade.key.RSHIFT


def test_invalid_key_name_falls_back_to_default_and_logs_warning(caplog) -> None:
    """Invalid setting key names should warn and use default binding."""
    manager = InputManager(GameSettings(key_fire="BAD_KEY"))

    assert manager.get_binding("fire") == arcade.key.SPACE
    assert "BAD_KEY" in caplog.text
    assert "falling back to default" in caplog.text


def test_key_name_map_contains_required_keys() -> None:
    """KEY_NAME_MAP should include required named keys, letters, and digits."""
    required_names = {
        "LEFT",
        "RIGHT",
        "UP",
        "DOWN",
        "SPACE",
        "LSHIFT",
        "RSHIFT",
        "ESCAPE",
        "ENTER",
        "BACKSPACE",
        "TAB",
    }
    assert required_names.issubset(KEY_NAME_MAP)

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        assert letter in KEY_NAME_MAP
    for digit in range(10):
        assert f"KEY_{digit}" in KEY_NAME_MAP
