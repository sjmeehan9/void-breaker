"""Tests for audio and rendering foundation components."""

from __future__ import annotations

from pathlib import Path

import asterax.app.src.audio.audio_manager as audio_module
import asterax.app.src.rendering.hud as hud_module
from asterax.app.src.audio.audio_manager import AudioManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.rendering.hud import HUDRenderer
from asterax.app.src.rendering.starfield import StarfieldRenderer


def test_audio_manager_initializes_with_empty_sound_directory(tmp_path: Path) -> None:
    """Audio manager should initialise cleanly when no sound assets are present."""
    sound_dir = tmp_path / "sounds"
    sound_dir.mkdir()

    manager = AudioManager(GameSettings(), sound_dir)

    assert manager._sounds == {}  # noqa: SLF001


def test_audio_manager_play_nonexistent_is_noop(tmp_path: Path) -> None:
    """Playing a missing sound should not raise errors."""
    manager = AudioManager(GameSettings(), tmp_path / "sounds")

    manager.play("nonexistent")


def test_audio_manager_update_settings_changes_effective_volume(tmp_path: Path) -> None:
    """Updated settings should be applied to future playback requests."""
    manager = AudioManager(
        GameSettings(master_volume=0.5, sfx_volume=0.5),
        tmp_path / "sounds",
    )
    manager._sounds["fire"] = object()  # type: ignore[assignment]  # noqa: SLF001

    call_volumes: list[float] = []
    original_play = audio_module.arcade.play_sound
    audio_module.arcade.play_sound = lambda sound, volume: call_volumes.append(
        volume
    )  # type: ignore[assignment]
    try:
        manager.play("fire")
        manager.update_settings(GameSettings(master_volume=0.2, sfx_volume=0.5))
        manager.play("fire")
    finally:
        audio_module.arcade.play_sound = original_play

    assert call_volumes == [0.25, 0.1]


def test_audio_manager_play_explosion_maps_size_to_sound_name(tmp_path: Path) -> None:
    """Explosion helper should route size labels to correct sound stems."""
    manager = AudioManager(GameSettings(), tmp_path / "sounds")

    played_names: list[str] = []
    original_play = manager.play
    manager.play = lambda name, volume_override=None: played_names.append(  # type: ignore[method-assign]
        name
    )
    try:
        manager.play_explosion("large")
        manager.play_explosion("MEDIUM")
        manager.play_explosion("invalid")
    finally:
        manager.play = original_play  # type: ignore[assignment]

    assert played_names == ["explode_large", "explode_medium", "explode_small"]


def test_audio_manager_wrapper_methods_route_to_expected_sound_names(
    tmp_path: Path,
) -> None:
    """Convenience methods should delegate to the correct base sound names."""
    manager = AudioManager(GameSettings(), tmp_path / "sounds")

    played_names: list[str] = []
    original_play = manager.play
    manager.play = lambda name, volume_override=None: played_names.append(  # type: ignore[method-assign]
        name
    )
    try:
        manager.play_fire()
        manager.play_enemy_fire()
        manager.play_enemy_explode()
        manager.play_pickup_currency()
        manager.play_pickup_buff()
        manager.play_shop_purchase()
        manager.play_shop_denied()
        manager.play_level_clear()
        manager.play_game_over()
        manager.play_menu_nav()
        manager.play_menu_select()
        manager.play_shield_low()
        manager.play_insurance_deduct()
    finally:
        manager.play = original_play  # type: ignore[assignment]

    assert played_names == [
        "fire",
        "enemy_fire",
        "enemy_explode",
        "pickup_currency",
        "pickup_buff",
        "shop_purchase",
        "shop_denied",
        "level_clear",
        "game_over",
        "menu_nav",
        "menu_select",
        "shield_low",
        "insurance_deduct",
    ]


def test_starfield_renderer_is_deterministic_and_counts_stars() -> None:
    """Starfield generation should be deterministic and match requested count."""
    first = StarfieldRenderer(width=320, height=240, star_count=30)
    second = StarfieldRenderer(width=320, height=240, star_count=30)

    assert len(first._stars) == 30  # noqa: SLF001
    assert first._stars == second._stars  # noqa: SLF001


def test_hud_draw_text_calls_arcade_draw_text() -> None:
    """draw_text should forward text rendering arguments to Arcade."""
    calls: list[tuple[object, ...]] = []
    original_draw_text = hud_module.arcade.draw_text
    hud_module.arcade.draw_text = lambda *args, **kwargs: calls.append(
        (args, tuple(sorted(kwargs.items())))
    )  # type: ignore[assignment]
    try:
        renderer = HUDRenderer(window_width=800, window_height=600)
        renderer.draw_text("Score", 10.0, 20.0)
    finally:
        hud_module.arcade.draw_text = original_draw_text

    assert len(calls) == 1


def test_hud_draw_value_reuses_cached_text_for_same_value() -> None:
    """draw_value should not recreate text objects when value is unchanged."""
    created_texts: list["FakeText"] = []

    class FakeText:
        def __init__(
            self,
            text: str,
            x: float,
            y: float,
            color: tuple[int, int, int],
            font_size: int,
            anchor_x: str,
            anchor_y: str,
        ) -> None:
            del x, y, color, font_size, anchor_x, anchor_y
            self.text = text
            self.draw_calls = 0
            created_texts.append(self)

        def draw(self) -> None:
            self.draw_calls += 1

    original_text = hud_module.arcade.Text
    hud_module.arcade.Text = FakeText  # type: ignore[assignment]
    try:
        renderer = HUDRenderer(window_width=800, window_height=600)
        renderer.draw_value("Score", 42, 10.0, 20.0)
        renderer.draw_value("Score", 42, 10.0, 20.0)
    finally:
        hud_module.arcade.Text = original_text

    assert len(created_texts) == 1
    assert created_texts[0].draw_calls == 2
