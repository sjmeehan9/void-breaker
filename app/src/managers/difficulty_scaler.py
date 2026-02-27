"""Difficulty preset application helpers."""

from __future__ import annotations

from asterax.app.src.config.difficulty_tables import (
    DifficultyPreset,
    apply_difficulty_preset,
    get_difficulty_params,
    parse_difficulty_preset,
)
from asterax.app.src.config.game_config import DifficultyParams


class DifficultyScaler:
    """Apply preset multipliers over per-level base difficulty parameters."""

    def apply_preset(
        self,
        base_params: DifficultyParams,
        preset: str | DifficultyPreset,
    ) -> DifficultyParams:
        """Return preset-adjusted parameters from a base level profile."""

        return apply_difficulty_preset(base_params, preset)

    def for_level(self, level: int, preset: str | DifficultyPreset) -> DifficultyParams:
        """Return preset-adjusted parameters for a given level."""

        normalized = parse_difficulty_preset(preset)
        return self.apply_preset(get_difficulty_params(level), normalized)
