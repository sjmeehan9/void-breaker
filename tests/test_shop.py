"""Comprehensive tests for ShopPhaseState and ShopNode — layout, collision,
re-centring, purchase flow, denied flow, and integration with combat loop.
"""

from __future__ import annotations

import math
from pathlib import Path
from types import SimpleNamespace

import arcade
import pytest
from asterax.app.src.config.game_config import (
    SHOP_LAYOUT_CONFIG,
    GamePhase,
    GameState,
    InsuranceTier,
    ShipState,
)
from asterax.app.src.config.upgrade_definitions import ALL_UPGRADES, get_upgrade_by_id
from asterax.app.src.entities.shop_node import ShopNode
from asterax.app.src.managers.currency_manager import CurrencyManager
from asterax.app.src.managers.insurance_manager import InsuranceManager
from asterax.app.src.managers.upgrade_manager import UpgradeManager
from asterax.app.src.states.combat import CombatPhaseState
from asterax.app.src.states.shop import ShopPhaseState

# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------


class _MachineStub:
    """Minimal state-machine stub recording switch_state calls."""

    def __init__(self) -> None:
        self.switched_to: object | None = None

    def switch_state(self, state: object) -> None:
        """Record the last state-switch request."""
        self.switched_to = state

    def push_state(self, state: object) -> None:
        """Ignore push (pause) calls in tests."""
        del state


class _InputStub:
    """Default non-interacting input manager stub."""

    def is_action_held(self, action: str) -> bool:
        """Return False for all actions."""
        del action
        return False


class _AudioStub:
    """Capture played sound names for assertion."""

    def __init__(self) -> None:
        self.played: list[str] = []

    def play(self, name: str) -> None:
        """Record the sound name."""
        self.played.append(name)


def _shop_texture(name: str) -> Path:
    """Resolve a texture path in the shop sprite directory."""
    return Path(__file__).resolve().parents[1] / "assets" / "sprites" / "shop" / name


def _make_shop_state(
    monkeypatch,
    *,
    currency: int = 500,
    current_level: int = 1,
    audio: _AudioStub | None = None,
) -> tuple[ShopPhaseState, _MachineStub, _AudioStub]:
    """Create and enter a ShopPhaseState with standard test window mocking."""
    audio = audio or _AudioStub()
    machine = _MachineStub()
    game_state = GameState(currency=currency, current_level=current_level)
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
    shop = ShopPhaseState(machine, game_state=game_state)
    shop.on_enter()
    return shop, machine, audio


# ---------------------------------------------------------------------------
# TestShopNodeCost
# ---------------------------------------------------------------------------


class TestShopNodeCost:
    """Verify ShopNode.calculate_cost for various levels."""

    def test_level_zero_returns_base_cost(self) -> None:
        """Level 0 cost should equal the definition's base_cost."""
        defn = get_upgrade_by_id("weapon_fire_rate")
        assert defn is not None
        node = ShopNode(
            texture_path=_shop_texture("orb_weapon.png"),
            center_x=0.0,
            center_y=0.0,
            upgrade_definition=defn,
        )
        assert node.calculate_cost(0) == 80

    def test_cost_scales_geometrically(self) -> None:
        """Cost at successive levels should follow base_cost * scaling^level."""
        defn = get_upgrade_by_id("weapon_fire_rate")
        assert defn is not None
        node = ShopNode(
            texture_path=_shop_texture("orb_weapon.png"),
            center_x=0.0,
            center_y=0.0,
            upgrade_definition=defn,
        )
        expected = [int(80 * (1.5**level)) for level in range(6)]
        for level, exp in enumerate(expected):
            assert node.calculate_cost(level) == exp

    def test_null_definition_returns_zero(self) -> None:
        """Node without an upgrade definition should return zero cost."""
        node = ShopNode(
            texture_path=_shop_texture("orb_insurance.png"),
            center_x=0.0,
            center_y=0.0,
            upgrade_definition=None,
            is_insurance_node=True,
        )
        assert node.calculate_cost(0) == 0


# ---------------------------------------------------------------------------
# TestShopNodeAffordability
# ---------------------------------------------------------------------------


class TestShopNodeAffordability:
    """Verify ShopNode.can_purchase with various currency/level combinations."""

    def test_affordable_returns_true(self) -> None:
        """Node should be purchasable when currency matches or exceeds cost."""
        defn = get_upgrade_by_id("weapon_fire_rate")
        assert defn is not None
        node = ShopNode(
            texture_path=_shop_texture("orb_weapon.png"),
            center_x=0.0,
            center_y=0.0,
            upgrade_definition=defn,
        )
        assert node.can_purchase(currency=80, current_level=0) is True
        assert node.can_purchase(currency=999, current_level=0) is True

    def test_unaffordable_returns_false(self) -> None:
        """Node should not be purchasable when currency is below cost."""
        defn = get_upgrade_by_id("weapon_fire_rate")
        assert defn is not None
        node = ShopNode(
            texture_path=_shop_texture("orb_weapon.png"),
            center_x=0.0,
            center_y=0.0,
            upgrade_definition=defn,
        )
        assert node.can_purchase(currency=79, current_level=0) is False

    def test_max_level_returns_false(self) -> None:
        """Node at max level should never be purchasable."""
        defn = get_upgrade_by_id("weapon_fire_rate")
        assert defn is not None
        node = ShopNode(
            texture_path=_shop_texture("orb_weapon.png"),
            center_x=0.0,
            center_y=0.0,
            upgrade_definition=defn,
        )
        assert node.can_purchase(currency=99999, current_level=defn.max_level) is False


# ---------------------------------------------------------------------------
# TestShopLayout
# ---------------------------------------------------------------------------


class TestShopLayout:
    """Verify _generate_node_layout produces correct circular positions."""

    def test_six_regular_nodes(self, monkeypatch) -> None:
        """Layout should produce exactly 6 regular nodes."""
        shop, _, _ = _make_shop_state(monkeypatch)
        assert len(shop._node_views) == 6

    def test_regular_nodes_on_circle(self, monkeypatch) -> None:
        """Regular nodes should all be at the configured radius from center."""
        shop, _, _ = _make_shop_state(monkeypatch)
        cx, cy = 640.0, 480.0
        radius = (
            min(1280.0, 960.0) * SHOP_LAYOUT_CONFIG.radius_fraction_of_min_dimension
        )
        for view in shop._node_views:
            dist = math.hypot(
                view.sprite.center_x - cx,
                view.sprite.center_y - cy,
            )
            assert dist == pytest.approx(radius, abs=1.0)

    def test_continue_button_triggers_via_enter(self, monkeypatch) -> None:
        """Enter key should trigger continue transition."""
        shop, machine, audio = _make_shop_state(monkeypatch, currency=100)
        shop.on_key_press(arcade.key.ENTER, 0)
        assert isinstance(machine.switched_to, CombatPhaseState)
        assert "level_clear" in audio.played


# ---------------------------------------------------------------------------
# TestRecentring
# ---------------------------------------------------------------------------


class TestRecentring:
    """Verify re-centring interpolation math."""

    def test_ease_out_at_known_points(self) -> None:
        """Quadratic ease-out should produce 0, 0.75, 1.0 at t=0, 0.5, 1.0."""
        assert ShopPhaseState._ease_out_quadratic(0.0) == pytest.approx(0.0)
        assert ShopPhaseState._ease_out_quadratic(0.5) == pytest.approx(0.75)
        assert ShopPhaseState._ease_out_quadratic(1.0) == pytest.approx(1.0)

    def test_recentre_reaches_center(self, monkeypatch) -> None:
        """After full duration, ship should be at exact screen center."""
        shop, _, _ = _make_shop_state(monkeypatch)
        assert shop.player_ship is not None
        shop.player_ship.center_x = 100.0
        shop.player_ship.center_y = 200.0
        shop._start_recentre()
        shop._update_recentre(0.5)  # exceeds 0.3 s duration
        assert not shop._is_recentring()
        assert shop.player_ship.center_x == pytest.approx(640.0)
        assert shop.player_ship.center_y == pytest.approx(480.0)

    def test_recentre_zeros_velocity(self, monkeypatch) -> None:
        """After re-centring completes, velocity should be zeroed."""
        shop, _, _ = _make_shop_state(monkeypatch)
        assert shop.player_ship is not None
        shop.player_ship.velocity_x = 150.0
        shop.player_ship.velocity_y = -80.0
        shop._start_recentre()
        shop._update_recentre(0.5)
        assert shop.player_ship.velocity_x == 0.0
        assert shop.player_ship.velocity_y == 0.0

    def test_midpoint_interpolation(self, monkeypatch) -> None:
        """At 50% of duration the position should follow the ease-out curve."""
        shop, _, _ = _make_shop_state(monkeypatch)
        assert shop.player_ship is not None
        start_x, start_y = 100.0, 200.0
        shop.player_ship.center_x = start_x
        shop.player_ship.center_y = start_y
        shop._start_recentre()
        # Advance by exactly half the duration
        half_duration = shop._recentre_duration / 2.0
        shop._update_recentre(half_duration)
        eased = ShopPhaseState._ease_out_quadratic(0.5)
        expected_x = start_x + (640.0 - start_x) * eased
        expected_y = start_y + (480.0 - start_y) * eased
        assert shop.player_ship.center_x == pytest.approx(expected_x, abs=1.0)
        assert shop.player_ship.center_y == pytest.approx(expected_y, abs=1.0)


# ---------------------------------------------------------------------------
# TestPurchaseFlow
# ---------------------------------------------------------------------------


class TestPurchaseFlow:
    """Verify the full purchase sequence: collision -> spend -> apply -> recentre."""

    def test_successful_purchase_deducts_and_upgrades(self, monkeypatch) -> None:
        """Colliding with an affordable node should spend and increment level."""
        shop, _, audio = _make_shop_state(monkeypatch, currency=200)
        upgrade_node = next(
            v.sprite
            for v in shop._node_views
            if not v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop.on_update(0.016)

        assert shop.game_state.currency < 200
        assert shop.game_state.run_stats.upgrades_purchased == 1
        assert "shop_purchase" in audio.played

    def test_purchase_triggers_recentre(self, monkeypatch) -> None:
        """Successful purchase should activate re-centring."""
        shop, _, _ = _make_shop_state(monkeypatch, currency=500)
        upgrade_node = next(
            v.sprite
            for v in shop._node_views
            if not v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop.on_update(0.016)
        assert shop._is_recentring()

    def test_recentre_blocks_further_purchases(self, monkeypatch) -> None:
        """During re-centring, node collisions should not trigger purchases."""
        shop, _, _ = _make_shop_state(monkeypatch, currency=5000)
        upgrade_node = next(
            v.sprite
            for v in shop._node_views
            if not v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop.on_update(0.016)
        before_currency = shop.game_state.currency
        # Force ship onto node during recentre
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop._handle_node_collisions()
        assert shop.game_state.currency == before_currency

    def test_insurance_purchase_cycles_tier(self, monkeypatch) -> None:
        """Colliding with insurance node should advance tier and spend."""
        shop, _, audio = _make_shop_state(monkeypatch, currency=500, current_level=2)
        ins_node = next(
            v.sprite for v in shop._node_views if v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = ins_node.center_x
        shop.player_ship.center_y = ins_node.center_y
        shop.on_update(0.016)
        assert shop.insurance_manager.get_tier() is InsuranceTier.BASIC
        assert shop.game_state.currency < 500
        assert "shop_purchase" in audio.played


# ---------------------------------------------------------------------------
# TestDeniedFlow
# ---------------------------------------------------------------------------


class TestDeniedFlow:
    """Verify that unaffordable collisions trigger denied sound only."""

    def test_denied_plays_sound_no_balance_change(self, monkeypatch) -> None:
        """Unaffordable node collision should play denied sound, balance unchanged."""
        shop, _, audio = _make_shop_state(monkeypatch, currency=0)
        upgrade_node = next(
            v.sprite
            for v in shop._node_views
            if not v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop.on_update(0.016)

        assert shop.game_state.currency == 0
        assert "shop_denied" in audio.played
        assert "shop_purchase" not in audio.played

    def test_denied_does_not_upgrade(self, monkeypatch) -> None:
        """Denied purchase should not change any upgrade levels."""
        shop, _, _ = _make_shop_state(monkeypatch, currency=0)
        assert shop.ship_state.weapon_fire_rate_level == 0
        upgrade_node = next(
            v.sprite
            for v in shop._node_views
            if not v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop.on_update(0.016)
        assert shop.ship_state.weapon_fire_rate_level == 0


# ---------------------------------------------------------------------------
# Integration: combat -> shop -> combat loop
# ---------------------------------------------------------------------------


class TestCombatShopCombatLoop:
    """Verify full combat->shop->combat transitions and state handoff."""

    def test_continue_transitions_to_combat_next_level(self, monkeypatch) -> None:
        """Continue should switch to CombatPhaseState at level + 1."""
        shop, machine, audio = _make_shop_state(
            monkeypatch, currency=100, current_level=3
        )
        shop.on_key_press(arcade.key.ENTER, 0)
        assert isinstance(machine.switched_to, CombatPhaseState)
        assert machine.switched_to.current_level == 4
        assert shop.game_state.phase == GamePhase.COMBAT
        assert "level_clear" in audio.played

    def test_shop_enters_at_shop_phase(self, monkeypatch) -> None:
        """On entry, shop should set game state phase to SHOP."""
        shop, _, _ = _make_shop_state(monkeypatch)
        assert shop.game_state.phase == GamePhase.SHOP

    def test_purchase_then_continue_preserves_upgrade(self, monkeypatch) -> None:
        """An upgrade purchased in shop should persist through continue."""
        shop, machine, _ = _make_shop_state(monkeypatch, currency=500)
        # Purchase an upgrade
        upgrade_node = next(
            v.sprite
            for v in shop._node_views
            if not v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop.on_update(0.016)
        assert shop.game_state.run_stats.upgrades_purchased == 1
        upgrade_level_after_purchase = shop.ship_state.weapon_fire_rate_level

        # Continue to next level
        # Wait for recentre to complete
        shop._update_recentre(1.0)
        shop.on_key_press(arcade.key.ENTER, 0)
        assert isinstance(machine.switched_to, CombatPhaseState)
        # Upgrade level should be preserved in the ship_state
        assert shop.ship_state.weapon_fire_rate_level == upgrade_level_after_purchase

    def test_continue_deducts_insurance_cost(self, monkeypatch) -> None:
        """Continue should deduct recurring insurance cost before transitioning."""
        shop, machine, _ = _make_shop_state(monkeypatch, currency=500, current_level=2)
        # Set insurance to BASIC
        shop.insurance_manager.set_tier(InsuranceTier.BASIC)
        balance_before = shop.game_state.currency

        shop.on_key_press(arcade.key.ENTER, 0)

        insurance_cost = shop.insurance_manager.get_tier_cost(InsuranceTier.BASIC, 2)
        expected_balance = balance_before - insurance_cost
        assert shop.game_state.currency == expected_balance
        assert isinstance(machine.switched_to, CombatPhaseState)


# ---------------------------------------------------------------------------
# Integration: cost scaling across 5 levels for all upgrade types
# ---------------------------------------------------------------------------


class TestCostScalingAllUpgrades:
    """Verify cost scaling is correct across 5 upgrade levels for all types."""

    @pytest.mark.parametrize(
        "upgrade_id",
        [defn.id for defn in ALL_UPGRADES],
        ids=[defn.id for defn in ALL_UPGRADES],
    )
    def test_shop_node_cost_matches_definition(self, upgrade_id: str) -> None:
        """ShopNode.calculate_cost should agree with upgrade definition scaling."""
        defn = get_upgrade_by_id(upgrade_id)
        assert defn is not None
        node = ShopNode(
            texture_path=_shop_texture("orb_weapon.png"),
            center_x=0.0,
            center_y=0.0,
            upgrade_definition=defn,
        )
        for level in range(min(5, defn.max_level)):
            expected = int(defn.base_cost * (defn.cost_scaling**level))
            assert node.calculate_cost(level) == expected


# ---------------------------------------------------------------------------
# Integration: insufficient currency denial leaves balance unchanged
# ---------------------------------------------------------------------------


class TestInsufficientCurrencyDenial:
    """Verify denied purchases leave balance exactly unchanged."""

    def test_denied_upgrade_preserves_exact_balance(self, monkeypatch) -> None:
        """Currency after a denied upgrade attempt should be identical to before."""
        shop, _, _ = _make_shop_state(monkeypatch, currency=10)
        balance_before = shop.game_state.currency
        upgrade_node = next(
            v.sprite
            for v in shop._node_views
            if not v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop.on_update(0.016)
        assert shop.game_state.currency == balance_before

    def test_denied_insurance_preserves_exact_balance(self, monkeypatch) -> None:
        """Currency after a denied insurance attempt should be identical."""
        shop, _, _ = _make_shop_state(monkeypatch, currency=0, current_level=5)
        balance_before = shop.game_state.currency
        ins_node = next(
            v.sprite for v in shop._node_views if v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = ins_node.center_x
        shop.player_ship.center_y = ins_node.center_y
        shop.on_update(0.016)
        assert shop.game_state.currency == balance_before


# ---------------------------------------------------------------------------
# Integration: multi-level run with shop usage
# ---------------------------------------------------------------------------


class TestMultiLevelRunE2E:
    """End-to-end scenario: multi-level run with shop purchases and insurance."""

    def test_three_level_run_with_upgrades_and_insurance(self, monkeypatch) -> None:
        """Simulate 3 shop visits: buy upgrade, buy insurance, continue with costs."""
        audio = _AudioStub()
        machine = _MachineStub()
        game_state = GameState(currency=2000, current_level=1)
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

        # --- Shop visit 1: purchase an upgrade ---
        shop = ShopPhaseState(machine, game_state=game_state)
        shop.on_enter()
        assert game_state.phase == GamePhase.SHOP

        upgrade_node = next(
            v.sprite
            for v in shop._node_views
            if not v.sprite.is_insurance_node
        )
        assert shop.player_ship is not None
        shop.player_ship.center_x = upgrade_node.center_x
        shop.player_ship.center_y = upgrade_node.center_y
        shop.on_update(0.016)
        assert game_state.run_stats.upgrades_purchased >= 1
        currency_after_purchase = game_state.currency

        # Continue to next level
        shop._update_recentre(1.0)
        shop.on_key_press(arcade.key.ENTER, 0)
        assert isinstance(machine.switched_to, CombatPhaseState)
        assert game_state.current_level == 2

        # --- Shop visit 2: buy insurance ---
        shop2 = ShopPhaseState(machine, game_state=game_state)
        shop2.on_enter()
        ins_node = next(
            v.sprite for v in shop2._node_views if v.sprite.is_insurance_node
        )
        assert shop2.player_ship is not None
        shop2.player_ship.center_x = ins_node.center_x
        shop2.player_ship.center_y = ins_node.center_y
        shop2.on_update(0.016)
        assert shop2.insurance_manager.get_tier() is InsuranceTier.BASIC

        # Continue — insurance cost deducted
        shop2._update_recentre(1.0)
        balance_before_continue = game_state.currency
        shop2.on_key_press(arcade.key.ENTER, 0)
        assert game_state.current_level == 3
        assert game_state.currency < balance_before_continue

        # --- Shop visit 3: verify stats persist, continue again ---
        shop3 = ShopPhaseState(machine, game_state=game_state)
        shop3.on_enter()
        shop3.on_key_press(arcade.key.ENTER, 0)
        assert game_state.current_level == 4
        assert game_state.run_stats.upgrades_purchased >= 1
