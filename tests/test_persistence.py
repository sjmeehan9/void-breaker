"""Tests for persistence schemas and file-backed persistence manager."""

import json
from pathlib import Path

from asterax.app.src.persistence.persistence_manager import PersistenceManager
from asterax.app.src.persistence.schemas import GameSettings, HighScoreEntry


def test_game_settings_defaults_match_spec() -> None:
    """GameSettings should expose the expected default schema values."""
    settings = GameSettings()

    assert settings.master_volume == 0.8
    assert settings.music_volume == 0.5
    assert settings.sfx_volume == 1.0
    assert settings.key_rotate_left == "LEFT"
    assert settings.key_rotate_right == "RIGHT"
    assert settings.key_thrust == "UP"
    assert settings.key_fire == "SPACE"
    assert settings.key_brake == "DOWN"
    assert settings.key_special == "LSHIFT"
    assert settings.key_pause == "ESCAPE"
    assert settings.fire_mode == "hold"
    assert settings.autofire is False
    assert settings.colorblind_mode is False
    assert settings.screen_shake == "medium"
    assert settings.difficulty == "classic"
    assert settings.fullscreen is False
    assert settings.resolution == (1280, 960)


def test_game_settings_round_trip_through_dict() -> None:
    """GameSettings should round-trip through dictionary serialisation."""
    settings = GameSettings(master_volume=0.3, resolution=(1920, 1080), autofire=True)

    restored = GameSettings.from_dict(settings.to_dict())

    assert restored == settings


def test_high_score_entry_round_trip_through_dict() -> None:
    """HighScoreEntry should round-trip through dictionary serialisation."""
    entry = HighScoreEntry(
        name="ACE",
        score=12345,
        level_reached=8,
        difficulty="classic",
        enemies_destroyed=22,
        currency_collected=800,
        currency_spent=500,
        date="2026-02-21T12:00:00",
    )

    restored = HighScoreEntry.from_dict(entry.to_dict())

    assert restored == entry


def test_load_settings_returns_defaults_when_missing(tmp_path: Path) -> None:
    """Missing settings file should load schema defaults."""
    manager = PersistenceManager(base_dir=tmp_path)

    assert manager.load_settings() == GameSettings()


def test_save_and_load_settings_round_trip(tmp_path: Path) -> None:
    """Saved settings should be read back accurately."""
    manager = PersistenceManager(base_dir=tmp_path)
    settings = GameSettings(
        master_volume=0.9,
        music_volume=0.25,
        sfx_volume=0.75,
        key_fire="F",
        fire_mode="tap",
        autofire=True,
        resolution=(1600, 900),
    )

    manager.save_settings(settings)

    assert manager.load_settings() == settings


def test_load_settings_with_corrupt_json_falls_back_to_defaults(tmp_path: Path) -> None:
    """Corrupt settings JSON should not crash and should return defaults."""
    manager = PersistenceManager(base_dir=tmp_path)
    (tmp_path / "settings.json").write_text("{not-valid-json", encoding="utf-8")

    assert manager.load_settings() == GameSettings()


def test_load_settings_with_missing_keys_uses_defaults(tmp_path: Path) -> None:
    """Settings payload with missing keys should preserve provided values and default others."""
    manager = PersistenceManager(base_dir=tmp_path)
    payload = {"version": 1, "master_volume": 0.2, "difficulty": "hard"}
    (tmp_path / "settings.json").write_text(json.dumps(payload), encoding="utf-8")

    settings = manager.load_settings()

    assert settings.master_volume == 0.2
    assert settings.difficulty == "hard"
    assert settings.key_fire == "SPACE"
    assert settings.resolution == (1280, 960)


def test_load_settings_with_future_version_falls_back_to_defaults(
    tmp_path: Path,
) -> None:
    """Future schema versions should fall back to defaults."""
    manager = PersistenceManager(base_dir=tmp_path)
    payload = {"version": 999, "master_volume": 0.2}
    (tmp_path / "settings.json").write_text(json.dumps(payload), encoding="utf-8")

    assert manager.load_settings() == GameSettings()


def test_save_and_load_high_scores_round_trip(tmp_path: Path) -> None:
    """Saved high score entries should load back accurately."""
    manager = PersistenceManager(base_dir=tmp_path)
    entries = [
        HighScoreEntry(
            name="ACE",
            score=1000,
            level_reached=3,
            difficulty="classic",
            enemies_destroyed=10,
            currency_collected=120,
            currency_spent=60,
            date="2026-02-21T18:30:00",
        ),
        HighScoreEntry(
            name="ZED",
            score=850,
            level_reached=2,
            difficulty="hard",
            enemies_destroyed=7,
            currency_collected=90,
            currency_spent=40,
            date="2026-02-21T18:35:00",
        ),
    ]

    manager.save_high_scores(entries)

    assert manager.load_high_scores() == entries


def test_load_high_scores_returns_empty_list_when_missing(tmp_path: Path) -> None:
    """Missing high score file should return an empty list."""
    manager = PersistenceManager(base_dir=tmp_path)

    assert manager.load_high_scores() == []


def test_save_is_atomic_and_leaves_no_temp_files(tmp_path: Path) -> None:
    """Atomic save should leave only the target JSON files in the directory."""
    manager = PersistenceManager(base_dir=tmp_path)
    manager.save_settings(GameSettings())
    manager.save_high_scores([])

    saved_files = sorted(path.name for path in tmp_path.iterdir())

    assert saved_files == ["high_scores.json", "settings.json"]
