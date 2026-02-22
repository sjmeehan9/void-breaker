"""Phase 2 scoring tests."""

from __future__ import annotations

from asterax.app.src.config.game_config import AsteroidSize
from asterax.app.src.managers.score_manager import ScoreManager


def test_score_per_asteroid_size() -> None:
    """Score manager should award configured points per asteroid tier."""
    manager = ScoreManager()
    assert manager.award_asteroid_points(AsteroidSize.LARGE) == 20
    assert manager.award_asteroid_points(AsteroidSize.MEDIUM) == 50
    assert manager.award_asteroid_points(AsteroidSize.SMALL) == 100
    assert manager.score == 170


def test_score_manager_reset() -> None:
    """Score reset should clear accumulated score for a new run."""
    manager = ScoreManager()
    manager.award_asteroid_points(AsteroidSize.SMALL)
    manager.reset()
    assert manager.score == 0
