"""Phase 5 audio trigger mapping tests."""

from __future__ import annotations

from pathlib import Path

from asterax.app.src.audio.audio_manager import AudioManager
from asterax.app.src.persistence.schemas import GameSettings


class _RecordingAudioManager(AudioManager):
    def __init__(self) -> None:
        super().__init__(GameSettings(), Path("/tmp/does-not-exist"))
        self.calls: list[str] = []

    def play(self, name: str, volume_override: float | None = None) -> None:
        del volume_override
        self.calls.append(name)


def test_audio_wrapper_methods_route_to_expected_sound_names() -> None:
    """All wrapper methods map to the expected logical sound identifiers."""
    manager = _RecordingAudioManager()
    manager.play_fire()
    manager.play_hit()
    manager.play_explosion("small")
    manager.play_explosion("medium")
    manager.play_explosion("large")
    manager.play_enemy_explode()
    manager.play_enemy_fire()
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

    assert manager.calls == [
        "fire",
        "hit",
        "explode_small",
        "explode_medium",
        "explode_large",
        "enemy_explode",
        "enemy_fire",
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
