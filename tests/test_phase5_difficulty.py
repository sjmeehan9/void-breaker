"""Phase 5 difficulty preset integration tests."""

from __future__ import annotations

from asterax.app.src.config.difficulty_tables import (
    DifficultyPreset,
    apply_difficulty_preset,
    get_difficulty_params,
)


def test_difficulty_presets_apply_expected_multiplier_direction() -> None:
    """Casual softens while hard increases pressure compared to classic baseline."""
    base = get_difficulty_params(12)
    casual = apply_difficulty_preset(base, DifficultyPreset.CASUAL)
    classic = apply_difficulty_preset(base, DifficultyPreset.CLASSIC)
    hard = apply_difficulty_preset(base, DifficultyPreset.HARD)

    assert casual.asteroid_count <= classic.asteroid_count <= hard.asteroid_count
    assert casual.enemy_aggression <= classic.enemy_aggression <= hard.enemy_aggression
    assert hard.enemy_spawn_interval <= classic.enemy_spawn_interval
    assert casual.currency_drop_chance >= classic.currency_drop_chance
