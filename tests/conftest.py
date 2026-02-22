"""Shared pytest fixtures for Phase 1 and Phase 2 test modules."""

from __future__ import annotations

from pathlib import Path

import pytest
from asterax.app.src.config.game_config import (
    ASTEROID_CONFIG,
    GAME_CONFIG,
    PHYSICS_CONFIG,
    AsteroidConfig,
    GameConfig,
    GameState,
    PhysicsConfig,
)
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.managers.currency_manager import CurrencyManager
from asterax.app.src.managers.entity_manager import EntityManager
from asterax.app.src.managers.score_manager import ScoreManager
from asterax.app.src.persistence.persistence_manager import PersistenceManager
from asterax.app.src.persistence.schemas import GameSettings
from asterax.app.src.physics.collisions import CollisionSystem
from asterax.app.src.states.state_machine import StateMachine


@pytest.fixture
def game_settings() -> GameSettings:
    """Return default game settings for tests."""
    return GameSettings()


@pytest.fixture
def persistence_manager(tmp_path) -> PersistenceManager:
    """Return a persistence manager rooted in a per-test temporary directory."""
    return PersistenceManager(base_dir=tmp_path)


@pytest.fixture
def input_manager(game_settings: GameSettings) -> InputManager:
    """Return an input manager initialised with default settings."""
    return InputManager(game_settings)


@pytest.fixture
def game_config() -> GameConfig:
    """Return the immutable game configuration singleton."""
    return GAME_CONFIG


@pytest.fixture
def game_state() -> GameState:
    """Return a default mutable game-state model for tests."""
    return GameState()


@pytest.fixture
def mock_state_machine() -> StateMachine:
    """Return an empty state machine instance for transition tests."""
    return StateMachine()


@pytest.fixture
def physics_config() -> PhysicsConfig:
    """Return shared physics configuration for gameplay tests."""
    return PHYSICS_CONFIG


@pytest.fixture
def asteroid_config() -> AsteroidConfig:
    """Return shared asteroid configuration for gameplay tests."""
    return ASTEROID_CONFIG


@pytest.fixture
def player_ship(physics_config: PhysicsConfig) -> PlayerShip:
    """Create a default player ship centered in a 1280x960 playfield."""
    sprite_path = (
        Path(__file__).resolve().parents[1] / "assets" / "sprites" / "ship.png"
    )
    return PlayerShip(
        sprite_path=sprite_path,
        center_x=640.0,
        center_y=480.0,
        physics_config=physics_config,
    )


@pytest.fixture
def entity_manager(player_ship: PlayerShip) -> EntityManager:
    """Return a fresh entity manager with an assigned player ship."""
    manager = EntityManager()
    manager.player_ship = player_ship
    return manager


@pytest.fixture
def collision_system() -> CollisionSystem:
    """Return a default collision system."""
    return CollisionSystem()


@pytest.fixture
def score_manager() -> ScoreManager:
    """Return a score manager initialized at zero."""
    return ScoreManager()


@pytest.fixture
def currency_manager() -> CurrencyManager:
    """Return a currency manager initialized at zero."""
    return CurrencyManager()
