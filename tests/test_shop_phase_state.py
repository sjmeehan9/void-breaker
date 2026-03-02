"""Focused tests for shop-phase layout, bounds clamping, and transitions."""

from __future__ import annotations

import math
from types import SimpleNamespace

import arcade
import pytest
from asterax.app.src.config.game_config import (
    SHOP_LAYOUT_CONFIG,
    GamePhase,
    GameState,
)
from asterax.app.src.states.combat import CombatPhaseState
from asterax.app.src.states.shop import ShopPhaseState


class _MachineStub:
    """Minimal state-machine stub capturing switch requests."""

    def __init__(self) -> None:
        self.switched_to: object | None = None

    def switch_state(self, state: object) -> None:
        self.switched_to = state

    def push_state(self, state: object) -> None:
        del state


class _InputStub:
    """Default non-interacting input manager stub."""

    def is_action_held(self, action: str) -> bool:
        del action
        return False


class _AudioStub:
    """Simple audio stub that records played sound names."""

    def __init__(self) -> None:
        self.played: list[str] = []

    def play(self, name: str) -> None:
        self.played.append(name)


def test_shop_on_enter_centers_ship_and_sets_phase(monkeypatch) -> None:
    """Shop entry should reset ship motion and mark run phase as shop."""
    machine = _MachineStub()
    run_state = GameState(current_level=3, currency=120)
    shop = ShopPhaseState(machine, game_state=run_state)
    monkeypatch.setattr(
        arcade,
        "get_window",
        lambda: SimpleNamespace(width=1280, height=960, input_manager=_InputStub()),
    )

    shop.on_enter()

    assert shop.player_ship is not None
    assert shop.player_ship.center_x == 640.0
    assert shop.player_ship.center_y == 480.0
    assert shop.player_ship.velocity_x == 0.0
    assert shop.player_ship.velocity_y == 0.0
    assert run_state.phase == GamePhase.SHOP


def test_shop_generate_node_layout_uses_circular_positions(monkeypatch) -> None:
    """Shop layout should place core nodes on a radius (no continue node)."""
    machine = _MachineStub()
    shop = ShopPhaseState(machine, game_state=GameState())
    monkeypatch.setattr(
        arcade,
        "get_window",
        lambda: SimpleNamespace(width=1280, height=960, input_manager=_InputStub()),
    )
    shop.on_enter()

    center_x = 640.0
    center_y = 480.0
    radius = min(1280.0, 960.0) * SHOP_LAYOUT_CONFIG.radius_fraction_of_min_dimension
    distances = [
        math.hypot(
            view.sprite.center_x - center_x, view.sprite.center_y - center_y
        )
        for view in shop._node_views
    ]

    assert len(shop._node_views) == 6
    assert all(distance == pytest.approx(radius, abs=0.6) for distance in distances)


def test_shop_clamp_ship_to_bounds() -> None:
    """Shop clamp should prevent ship movement beyond screen edges."""
    shop = ShopPhaseState(_MachineStub(), game_state=GameState())
    shop.player_ship = SimpleNamespace(center_x=-25.0, center_y=1300.0)

    shop._clamp_ship_to_bounds(1280.0, 960.0)

    assert shop.player_ship.center_x == 0.0
    assert shop.player_ship.center_y == 960.0


def test_shop_enter_key_transitions_back_to_combat(monkeypatch) -> None:
    """Pressing enter in shop should start the next combat level."""
    machine = _MachineStub()
    run_state = GameState(current_level=4, score=900, currency=85)
    shop = ShopPhaseState(machine, game_state=run_state)
    audio = _AudioStub()
    monkeypatch.setattr(
        arcade,
        "get_window",
        lambda: SimpleNamespace(
            width=1280,
            height=960,
            input_manager=_InputStub(),
            audio_manager=audio,
        ),
    )
    shop.on_enter()

    shop.on_key_press(arcade.key.ENTER, 0)

    assert isinstance(machine.switched_to, CombatPhaseState)
    assert machine.switched_to.current_level == 5
    assert run_state.phase == GamePhase.COMBAT
    assert "level_clear" in audio.played


def test_shop_recentre_reaches_exact_center_and_zeros_velocity(monkeypatch) -> None:
    """Re-centering should end exactly at screen center with no residual drift."""
    machine = _MachineStub()
    run_state = GameState(current_level=2, currency=500)
    shop = ShopPhaseState(machine, game_state=run_state)
    monkeypatch.setattr(
        arcade,
        "get_window",
        lambda: SimpleNamespace(
            width=1280,
            height=960,
            input_manager=_InputStub(),
            audio_manager=_AudioStub(),
        ),
    )
    shop.on_enter()
    assert shop.player_ship is not None
    shop.player_ship.center_x = 200.0
    shop.player_ship.center_y = 100.0
    shop.player_ship.velocity_x = 120.0
    shop.player_ship.velocity_y = -90.0

    shop._start_recentre()  # noqa: SLF001
    shop._update_recentre(0.3)  # noqa: SLF001

    assert not shop._is_recentring()  # noqa: SLF001
    assert shop.player_ship.center_x == pytest.approx(640.0)
    assert shop.player_ship.center_y == pytest.approx(480.0)
    assert shop.player_ship.velocity_x == 0.0
    assert shop.player_ship.velocity_y == 0.0


def test_shop_recentre_blocks_collision_purchases(monkeypatch) -> None:
    """No purchases should trigger while re-centering is active."""
    machine = _MachineStub()
    run_state = GameState(current_level=3, currency=600)
    shop = ShopPhaseState(machine, game_state=run_state)
    monkeypatch.setattr(
        arcade,
        "get_window",
        lambda: SimpleNamespace(
            width=1280,
            height=960,
            input_manager=_InputStub(),
            audio_manager=_AudioStub(),
        ),
    )
    shop.on_enter()
    assert shop.player_ship is not None

    purchasable_node = next(
        view.sprite
        for view in shop._node_views  # noqa: SLF001
        if not view.sprite.is_insurance_node
    )
    shop.player_ship.center_x = purchasable_node.center_x
    shop.player_ship.center_y = purchasable_node.center_y

    before_currency = run_state.currency
    shop._start_recentre()  # noqa: SLF001
    shop._handle_node_collisions()  # noqa: SLF001

    assert run_state.currency == before_currency
    assert shop.ship_state.weapon_fire_rate_level == 0


def test_shop_ease_out_curve_known_points() -> None:
    """Quadratic ease-out should match expected values at key points."""
    assert ShopPhaseState._ease_out_quadratic(0.0) == pytest.approx(0.0)  # noqa: SLF001
    assert ShopPhaseState._ease_out_quadratic(0.5) == pytest.approx(
        0.75
    )  # noqa: SLF001
    assert ShopPhaseState._ease_out_quadratic(1.0) == pytest.approx(1.0)  # noqa: SLF001
