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
    """Shop layout should place core nodes on a radius with continue below ring."""
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
    regular_nodes = [
        view for view in shop._node_views if not view.is_continue
    ]  # noqa: SLF001
    continue_node = next(
        view for view in shop._node_views if view.is_continue  # noqa: SLF001
    )
    distances = [
        math.hypot(node.sprite.center_x - center_x, node.sprite.center_y - center_y)
        for node in regular_nodes
    ]

    assert len(regular_nodes) == 6
    assert all(distance == pytest.approx(radius, abs=0.6) for distance in distances)
    assert continue_node.sprite.center_x == pytest.approx(center_x)
    assert continue_node.sprite.center_y < center_y - radius


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
    monkeypatch.setattr(
        arcade,
        "get_window",
        lambda: SimpleNamespace(width=1280, height=960, input_manager=_InputStub()),
    )
    shop.on_enter()

    shop.on_key_press(arcade.key.ENTER, 0)

    assert isinstance(machine.switched_to, CombatPhaseState)
    assert machine.switched_to.current_level == 5
    assert run_state.phase == GamePhase.COMBAT
