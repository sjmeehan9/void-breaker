"""Phase 2 currency manager and pickup collection tests."""

from __future__ import annotations

import random

from asterax.app.src.config.game_config import GameState
from asterax.app.src.entities.pickups import CurrencyPickup
from asterax.app.src.managers.currency_manager import CurrencyManager
from asterax.app.src.managers.score_manager import ScoreManager
from asterax.app.src.managers.spawn_manager import SpawnManager
from asterax.app.src.physics.collisions import CollisionSystem


def test_currency_pickup_collection(entity_manager) -> None:
    """Ship collision with a pickup should increase currency balance."""
    pickup = CurrencyPickup(
        center_x=entity_manager.player_ship.center_x,
        center_y=entity_manager.player_ship.center_y,
        value=10,
        drift_speed_range=(0.0, 0.0),
    )
    entity_manager.currency_pickups.append(pickup)
    game_state = GameState()
    currency_manager = CurrencyManager()

    CollisionSystem().check_all(
        entity_manager=entity_manager,
        game_state=game_state,
        spawn_manager=SpawnManager(rng=random.Random(8)),
        score_manager=ScoreManager(),
        screen_width=1280.0,
        screen_height=960.0,
        currency_manager=currency_manager,
    )

    assert game_state.currency == 10
    assert currency_manager.get_balance() == 10


def test_currency_manager_earn_spend(currency_manager) -> None:
    """Currency manager should track earning, spending, and failed spends."""
    currency_manager.earn(30)
    assert currency_manager.spend(10) is True
    assert currency_manager.spend(40) is False
    assert currency_manager.get_balance() == 20
