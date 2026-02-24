"""Unit tests for shop node pricing, affordability, and interaction states."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import arcade
from asterax.app.src.config.game_config import GameState
from asterax.app.src.config.upgrade_definitions import get_upgrade_by_id
from asterax.app.src.entities.shop_node import ContinueNode, ShopNode
from asterax.app.src.states.shop import ShopPhaseState


class _MachineStub:
    """Minimal state-machine stub for shop tests."""

    def switch_state(self, state: object) -> None:
        del state

    def push_state(self, state: object) -> None:
        del state


class _InputStub:
    """Default non-interacting input manager stub."""

    def is_action_held(self, action: str) -> bool:
        del action
        return False


class _AudioStub:
    """Capture played sound names for assertion."""

    def __init__(self) -> None:
        self.played: list[str] = []

    def play(self, name: str) -> None:
        self.played.append(name)


def _shop_texture(path_name: str) -> Path:
    """Resolve a texture path under the shop sprite directory."""
    return (
        Path(__file__).resolve().parents[1] / "assets" / "sprites" / "shop" / path_name
    )


def test_shop_node_calculate_cost_and_can_purchase() -> None:
    """Cost scaling and affordability should follow upgrade rules."""
    definition = get_upgrade_by_id("weapon_fire_rate")
    assert definition is not None
    node = ShopNode(
        texture_path=_shop_texture("orb_weapon.png"),
        center_x=0.0,
        center_y=0.0,
        upgrade_definition=definition,
    )

    assert node.calculate_cost(0) == 50
    assert node.calculate_cost(1) == 75
    assert node.calculate_cost(2) == 112
    assert node.can_purchase(currency=112, current_level=2)
    assert not node.can_purchase(currency=111, current_level=2)
    assert not node.can_purchase(currency=999, current_level=definition.max_level)


def test_continue_node_is_always_purchasable() -> None:
    """Continue node should always report as available."""
    node = ContinueNode(
        texture_path=_shop_texture("node_continue.png"),
        center_x=0.0,
        center_y=0.0,
        upgrade_definition=None,
    )

    assert node.can_purchase(currency=0, current_level=0)
    assert node.can_purchase(currency=9999, current_level=99)


def test_shop_node_update_visual_state_sets_expected_alpha() -> None:
    """Visual alpha should reflect affordable, unaffordable, and maxed states."""
    definition = get_upgrade_by_id("weapon_fire_rate")
    assert definition is not None
    node = ShopNode(
        texture_path=_shop_texture("orb_weapon.png"),
        center_x=0.0,
        center_y=0.0,
        upgrade_definition=definition,
    )

    node.update_visual_state(currency=0, current_level=0, delta_time=0.1)
    assert node.alpha == 100

    node.update_visual_state(currency=9999, current_level=0, delta_time=0.1)
    assert 200 <= node.alpha <= 255

    node.update_visual_state(
        currency=9999,
        current_level=definition.max_level,
        delta_time=0.1,
    )
    assert node.alpha == 150


def test_shop_phase_collision_purchases_upgrade(monkeypatch) -> None:
    """Colliding with an affordable node should spend credits and upgrade stats."""
    audio_stub = _AudioStub()
    monkeypatch.setattr(
        arcade,
        "get_window",
        lambda: SimpleNamespace(
            width=1280,
            height=960,
            input_manager=_InputStub(),
            audio_manager=audio_stub,
        ),
    )

    state = ShopPhaseState(_MachineStub(), game_state=GameState(currency=200))
    state.on_enter()
    target_node = next(
        view.sprite for view in state._node_views if not view.is_continue
    )  # noqa: SLF001
    state.player_ship.center_x = target_node.center_x  # type: ignore[union-attr]
    state.player_ship.center_y = target_node.center_y  # type: ignore[union-attr]

    state.on_update(0.016)

    assert state.game_state.currency == 150
    assert state.ship_state.weapon_fire_rate_level == 1
    assert state.game_state.run_stats.currency_spent == 50
    assert state.game_state.run_stats.upgrades_purchased == 1
    assert "shop_purchase" in audio_stub.played
