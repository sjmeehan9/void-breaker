"""Tests for Phase 5.9 difficulty preset integration."""

from __future__ import annotations

import pytest
from asterax.app.src.config.difficulty_tables import DifficultyPreset
from asterax.app.src.config.game_config import DifficultyParams
from asterax.app.src.managers.difficulty_scaler import DifficultyScaler
from asterax.app.src.persistence.schemas import HighScoreEntry


def _base_params() -> DifficultyParams:
    """Return a representative baseline for preset application tests."""
    return DifficultyParams(
        asteroid_count=10,
        asteroid_speed_min=50.0,
        asteroid_speed_max=150.0,
        enemy_spawn_enabled=True,
        enemy_count_max=4,
        enemy_spawn_interval=5.0,
        enemy_aggression=0.5,
        aggressive_ratio=0.4,
        currency_drop_chance=0.4,
        currency_value_base=12,
    )


def test_apply_preset_casual_reduces_pressure_and_increases_currency() -> None:
    """Casual preset should lower combat pressure and increase drop chance."""
    scaler = DifficultyScaler()
    adjusted = scaler.apply_preset(_base_params(), DifficultyPreset.CASUAL)

    assert adjusted.asteroid_count == 7
    assert adjusted.enemy_aggression == 0.3
    assert adjusted.currency_drop_chance == pytest.approx(0.6)
    assert adjusted.enemy_spawn_interval == 7.0


def test_apply_preset_classic_keeps_parameters_unchanged() -> None:
    """Classic preset should preserve baseline level parameters."""
    scaler = DifficultyScaler()
    base = _base_params()
    adjusted = scaler.apply_preset(base, DifficultyPreset.CLASSIC)

    assert adjusted == base


def test_apply_preset_hard_increases_pressure_and_reduces_currency() -> None:
    """Hard preset should increase pressure and reduce currency drop chance."""
    scaler = DifficultyScaler()
    adjusted = scaler.apply_preset(_base_params(), DifficultyPreset.HARD)

    assert adjusted.asteroid_count == 14
    assert adjusted.enemy_aggression == 0.65
    assert adjusted.currency_drop_chance == pytest.approx(0.28)
    assert adjusted.enemy_spawn_interval == 3.5


def test_apply_preset_clamps_asteroids_and_aggression() -> None:
    """Preset application should clamp asteroid count and aggression to valid bounds."""
    scaler = DifficultyScaler()
    params = DifficultyParams(
        asteroid_count=1,
        enemy_aggression=0.95,
        aggressive_ratio=0.95,
        currency_drop_chance=0.02,
        enemy_spawn_interval=0.05,
    )

    adjusted = scaler.apply_preset(params, DifficultyPreset.HARD)

    assert adjusted.asteroid_count >= 1
    assert 0.0 <= adjusted.enemy_aggression <= 1.0
    assert 0.0 <= adjusted.aggressive_ratio <= 1.0
    assert adjusted.currency_drop_chance >= 0.05
    assert adjusted.enemy_spawn_interval >= 0.1


def test_high_score_entry_defaults_missing_difficulty_to_classic() -> None:
    """Legacy high-score payloads without difficulty should remain loadable."""
    entry = HighScoreEntry.from_dict(
        {
            "name": "AAA",
            "score": 1000,
            "level_reached": 5,
            "enemies_destroyed": 10,
            "currency_collected": 50,
            "currency_spent": 40,
            "date": "2026-02-28",
        }
    )

    assert entry.difficulty == "classic"
