"""Tests for visual transitions, screen shake, and colorblind palette helpers."""

from __future__ import annotations

import math

from asterax.app.src.rendering.transitions import (
    COLORBLIND_PALETTE,
    ScreenShake,
    TransitionEffect,
    palette_is_distinguishable,
)


def test_transition_effect_progresses_through_phases() -> None:
    """Transition should remain active for fade/hold/fade and complete at ~1.4s."""
    effect = TransitionEffect(width=1280, height=960)
    effect.start_level_transition(3)

    assert effect.is_active
    assert not effect.update(0.29)
    assert effect.is_active

    assert not effect.update(0.6)
    assert effect.is_active

    assert effect.update(0.51)
    assert not effect.is_active


def test_screen_shake_off_returns_zero_offset() -> None:
    """Off preset should never produce non-zero shake offset."""
    shake = ScreenShake()
    shake.trigger("off")
    shake.update(0.016)

    assert shake.get_offset() == (0.0, 0.0)


def test_screen_shake_decays_to_near_zero_after_half_second() -> None:
    """Shake should decay to near-zero offsets within configured duration window."""
    shake = ScreenShake()
    shake.trigger("medium")

    for _ in range(35):
        shake.update(0.016)

    x, y = shake.get_offset()
    assert math.hypot(x, y) <= 0.6


def test_screen_shake_intensity_matches_level_caps() -> None:
    """Low and medium shake offsets should remain within their max pixel ranges."""
    low_shake = ScreenShake()
    low_shake.trigger("low")
    for _ in range(5):
        low_shake.update(0.016)
        low_x, low_y = low_shake.get_offset()
        assert abs(low_x) <= 3.0
        assert abs(low_y) <= 3.0

    medium_shake = ScreenShake()
    medium_shake.trigger("medium")
    for _ in range(5):
        medium_shake.update(0.016)
        med_x, med_y = medium_shake.get_offset()
        assert abs(med_x) <= 8.0
        assert abs(med_y) <= 8.0


def test_colorblind_palette_contains_required_entity_mappings() -> None:
    """Palette should provide explicit mappings for all major gameplay entities."""
    required_keys = {
        "player",
        "asteroid",
        "enemy",
        "player_projectile",
        "enemy_projectile",
        "currency",
        "buff_heal",
        "buff_damage",
        "buff_speed",
        "shop_weapon",
        "shop_defense",
        "shop_mobility",
        "shop_economy",
        "shop_repair",
        "shop_insurance",
        "shop_continue",
    }
    assert required_keys.issubset(COLORBLIND_PALETTE.keys())
    assert palette_is_distinguishable()
