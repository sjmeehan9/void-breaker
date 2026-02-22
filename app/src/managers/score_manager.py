"""Score accumulation manager for combat outcomes."""

from __future__ import annotations

from asterax.app.src.config.game_config import ASTEROID_CONFIG, AsteroidSize


class ScoreManager:
    """Track and mutate player score totals."""

    def __init__(self) -> None:
        """Initialize score at zero."""
        self.score: int = 0

    def award_asteroid_points(self, asteroid_size: AsteroidSize) -> int:
        """Award points for a destroyed asteroid.

        Args:
            asteroid_size: Destroyed asteroid tier.

        Returns:
            Points awarded for this asteroid.
        """
        points = ASTEROID_CONFIG.point_values[asteroid_size]
        self.score += points
        return points

    def reset(self) -> None:
        """Reset score for a new run."""
        self.score = 0
