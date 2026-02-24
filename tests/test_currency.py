"""Phase 4.6 currency manager and economy flow tests."""

from __future__ import annotations

import random

import pytest
from asterax.app.src.config.game_config import GameState
from asterax.app.src.entities.pickups import CurrencyPickup
from asterax.app.src.managers.currency_manager import CurrencyManager, CurrencyRunStats
from asterax.app.src.managers.score_manager import ScoreManager
from asterax.app.src.managers.spawn_manager import SpawnManager
from asterax.app.src.physics.collisions import CollisionSystem


# ---------------------------------------------------------------------------
# Integration: pickup collection routes through CurrencyManager
# ---------------------------------------------------------------------------


def test_currency_pickup_collection(entity_manager) -> None:
    """Ship collision with a pickup should increase currency via the manager."""
    pickup = CurrencyPickup(
        center_x=entity_manager.player_ship.center_x,
        center_y=entity_manager.player_ship.center_y,
        value=10,
        drift_speed_range=(0.0, 0.0),
    )
    entity_manager.currency_pickups.append(pickup)
    game_state = GameState()
    currency_manager = CurrencyManager(game_state)

    CollisionSystem().check_all(
        entity_manager=entity_manager,
        game_state=game_state,
        spawn_manager=SpawnManager(rng=random.Random(8)),
        score_manager=ScoreManager(),
        screen_width=1280.0,
        screen_height=960.0,
        currency_manager=currency_manager,
    )

    # Both the manager's logical balance and game_state.currency must agree.
    assert currency_manager.get_balance() == 10
    assert game_state.currency == 10


# ---------------------------------------------------------------------------
# Unit: earn / spend basic behaviour (standalone — no GameState coupling)
# ---------------------------------------------------------------------------


def test_currency_manager_earn_spend(currency_manager) -> None:
    """Currency manager should track earning, spending, and failed spends."""
    currency_manager.earn(30)
    assert currency_manager.spend(10) is True
    assert currency_manager.spend(40) is False
    assert currency_manager.get_balance() == 20


# ---------------------------------------------------------------------------
# Phase 4.6 — comprehensive unit tests
# ---------------------------------------------------------------------------


def test_earn_increases_balance_and_total_earned() -> None:
    """earn() must add to balance and increment total_earned."""
    m = CurrencyManager()
    m.earn(100)
    assert m.get_balance() == 100
    assert m.total_earned == 100


def test_spend_true_deducts_and_tracks_total_spent() -> None:
    """spend() must deduct and return True when affordable."""
    m = CurrencyManager()
    m.earn(200)
    assert m.spend(50) is True
    assert m.get_balance() == 150
    assert m.total_spent == 50


def test_spend_false_leaves_state_unchanged() -> None:
    """spend() must return False and not modify balance when unaffordable."""
    m = CurrencyManager()
    m.earn(30)
    result = m.spend(100)
    assert result is False
    assert m.get_balance() == 30
    assert m.total_spent == 0


def test_can_spend_is_read_only() -> None:
    """can_spend() must not alter the balance regardless of the outcome."""
    m = CurrencyManager()
    m.earn(50)
    assert m.can_spend(50) is True
    assert m.can_spend(51) is False
    assert m.get_balance() == 50  # unchanged


def test_balance_never_goes_negative() -> None:
    """A sequence of mixed earn/spend calls must never produce a negative balance."""
    m = CurrencyManager()
    m.earn(100)
    m.spend(80)
    m.spend(50)  # should fail silently
    assert m.get_balance() >= 0


def test_deduct_behaves_identically_to_spend() -> None:
    """deduct() is a semantic alias for spend() and tracks total_spent."""
    m = CurrencyManager()
    m.earn(100)
    assert m.deduct(40) is True
    assert m.get_balance() == 60
    assert m.total_spent == 40
    assert m.deduct(100) is False
    assert m.get_balance() == 60


def test_get_run_stats_returns_correct_cumulative_values() -> None:
    """get_run_stats() must reflect the cumulative earn/spend history."""
    m = CurrencyManager()
    m.earn(500)
    m.spend(200)
    m.spend(400)  # fails — balance only 300
    stats = m.get_run_stats()
    assert isinstance(stats, CurrencyRunStats)
    assert stats.total_earned == 500
    assert stats.total_spent == 200


def test_earn_zero_raises_value_error() -> None:
    """earn(0) must raise ValueError."""
    m = CurrencyManager()
    with pytest.raises(ValueError, match="positive integer"):
        m.earn(0)


def test_earn_negative_raises_value_error() -> None:
    """earn(-1) must raise ValueError."""
    m = CurrencyManager()
    with pytest.raises(ValueError, match="positive integer"):
        m.earn(-1)


def test_spend_zero_raises_value_error() -> None:
    """spend(0) must raise ValueError."""
    m = CurrencyManager()
    m.earn(10)
    with pytest.raises(ValueError, match="positive integer"):
        m.spend(0)


def test_can_spend_zero_raises_value_error() -> None:
    """can_spend(0) must raise ValueError."""
    m = CurrencyManager()
    m.earn(10)
    with pytest.raises(ValueError, match="positive integer"):
        m.can_spend(0)


def test_reset_zeroes_balance_and_counters() -> None:
    """reset() must clear balance, total_earned, and total_spent."""
    m = CurrencyManager()
    m.earn(200)
    m.spend(50)
    m.reset()
    assert m.get_balance() == 0
    assert m.total_earned == 0
    assert m.total_spent == 0


def test_reset_with_game_state_zeroes_game_state_currency() -> None:
    """reset() on a manager wrapping GameState must zero game_state.currency."""
    gs = GameState()
    gs.currency = 150
    m = CurrencyManager(gs)
    m.reset()
    assert gs.currency == 0
    assert m.get_balance() == 0


def test_game_state_backed_manager_syncs_both_sides() -> None:
    """When backed by GameState, earn/spend must keep game_state.currency in sync."""
    gs = GameState()
    m = CurrencyManager(gs)
    m.earn(300)
    assert gs.currency == 300
    m.spend(100)
    assert gs.currency == 200
    assert m.get_balance() == 200


def test_full_economy_cycle() -> None:
    """Programmatic: earn 500, spend 200, fail spend 400, check balance = 300."""
    m = CurrencyManager()
    m.earn(500)
    assert m.spend(200) is True
    assert m.spend(400) is False
    assert m.get_balance() == 300
    stats = m.get_run_stats()
    assert stats.total_earned == 500
    assert stats.total_spent == 200
