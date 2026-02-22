"""Shared pytest fixtures for Phase 1 test modules."""

from __future__ import annotations

import pytest
from asterax.app.src.config.game_config import GAME_CONFIG, GameConfig, GameState
from asterax.app.src.input.input_manager import InputManager
from asterax.app.src.persistence.persistence_manager import PersistenceManager
from asterax.app.src.persistence.schemas import GameSettings
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
