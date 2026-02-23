"""Tests for SpawnManager enemy spawning functionality (Phase 3 Component 3.4)."""

from __future__ import annotations

import random

from asterax.app.src.config.enemy_config import EnemyArchetype
from asterax.app.src.config.game_config import DifficultyParams
from asterax.app.src.managers.spawn_manager import SpawnManager


def test_no_spawn_when_enemy_spawning_disabled() -> None:
    """Enemy spawning returns empty list when enemy_spawn_enabled=False."""
    manager = SpawnManager(rng=random.Random(42))
    params = DifficultyParams(
        enemy_spawn_enabled=False,
        enemy_count_max=5,
        enemy_spawn_interval=1.0,
        aggressive_ratio=0.5,
    )

    # Simulate passage of time beyond spawn interval
    enemies = manager.update_enemy_spawning(
        dt=2.0,
        current_enemy_count=0,
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert len(enemies) == 0


def test_no_spawn_before_interval_elapsed() -> None:
    """No enemy spawns before spawn_interval has elapsed."""
    manager = SpawnManager(rng=random.Random(42))
    params = DifficultyParams(
        enemy_spawn_enabled=True,
        enemy_count_max=5,
        enemy_spawn_interval=5.0,
        aggressive_ratio=0.3,
    )

    # First update: 2 seconds, not enough time
    enemies = manager.update_enemy_spawning(
        dt=2.0,
        current_enemy_count=0,
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )
    assert len(enemies) == 0

    # Second update: 2 more seconds, still not enough
    enemies = manager.update_enemy_spawning(
        dt=2.0,
        current_enemy_count=0,
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )
    assert len(enemies) == 0


def test_spawn_after_interval_when_enabled_and_under_cap() -> None:
    """Enemy spawns when interval elapsed, spawning enabled, and under cap."""
    manager = SpawnManager(rng=random.Random(42))
    params = DifficultyParams(
        enemy_spawn_enabled=True,
        enemy_count_max=5,
        enemy_spawn_interval=3.0,
        aggressive_ratio=0.3,
        enemy_aggression=0.5,
    )

    # Simulate 3+ seconds passing
    enemies = manager.update_enemy_spawning(
        dt=3.5,
        current_enemy_count=2,  # Under cap
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert len(enemies) == 1
    enemy = enemies[0]
    assert enemy.archetype in [EnemyArchetype.BASIC, EnemyArchetype.AGGRESSIVE]
    assert enemy.health > 0.0
    assert enemy.velocity_x != 0.0 or enemy.velocity_y != 0.0


def test_no_spawn_when_at_count_cap() -> None:
    """No enemy spawns when current count equals or exceeds max."""
    manager = SpawnManager(rng=random.Random(42))
    params = DifficultyParams(
        enemy_spawn_enabled=True,
        enemy_count_max=3,
        enemy_spawn_interval=1.0,
        aggressive_ratio=0.5,
    )

    # At cap
    enemies = manager.update_enemy_spawning(
        dt=2.0,
        current_enemy_count=3,
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )
    assert len(enemies) == 0

    # Above cap
    enemies = manager.update_enemy_spawning(
        dt=2.0,
        current_enemy_count=5,
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )
    assert len(enemies) == 0


def test_get_spawn_edge_position_returns_offscreen_with_inward_velocity() -> None:
    """Spawn edge position is off-screen and velocity points inward."""
    manager = SpawnManager(rng=random.Random(42))
    screen_width = 1280.0
    screen_height = 960.0

    # Test multiple spawn iterations to cover all edges
    for _ in range(20):
        x, y, vx, vy = manager._get_spawn_edge_position(
            speed=100.0,
            screen_width=screen_width,
            screen_height=screen_height,
        )

        # Position should be off-screen (outside bounds with margin)
        is_offscreen = (
            x < -40.0
            or x > screen_width + 40.0
            or y < -40.0
            or y > screen_height + 40.0
        )
        assert is_offscreen, f"Position ({x}, {y}) is not off-screen"

        # Velocity should have reasonable magnitude (approximately speed)
        velocity_magnitude = (vx**2 + vy**2) ** 0.5
        assert (
            80.0 <= velocity_magnitude <= 120.0
        ), f"Velocity magnitude {velocity_magnitude} outside expected range"

        # Velocity should point generally toward screen center
        center_x = screen_width / 2.0
        center_y = screen_height / 2.0
        direction_to_center_x = center_x - x
        direction_to_center_y = center_y - y

        # Dot product should be positive (velocity aligned with direction to center)
        dot_product = vx * direction_to_center_x + vy * direction_to_center_y
        assert (
            dot_product > 0.0
        ), f"Velocity ({vx}, {vy}) not pointing toward center from ({x}, {y})"


def test_select_archetype_respects_aggressive_ratio() -> None:
    """Archetype selection reflects aggressive_ratio statistically."""
    manager = SpawnManager(rng=random.Random(42))

    # Test with 0.0 aggressive_ratio (all basic)
    params_all_basic = DifficultyParams(aggressive_ratio=0.0)
    basic_count = 0
    for _ in range(100):
        archetype = manager._select_archetype(params_all_basic)
        if archetype == EnemyArchetype.BASIC:
            basic_count += 1
    assert basic_count == 100, "Expected all BASIC with aggressive_ratio=0.0"

    # Test with 1.0 aggressive_ratio (all aggressive)
    params_all_aggressive = DifficultyParams(aggressive_ratio=1.0)
    aggressive_count = 0
    for _ in range(100):
        archetype = manager._select_archetype(params_all_aggressive)
        if archetype == EnemyArchetype.AGGRESSIVE:
            aggressive_count += 1
    assert aggressive_count == 100, "Expected all AGGRESSIVE with aggressive_ratio=1.0"

    # Test with 0.5 aggressive_ratio (approximately 50/50 split)
    manager_mixed = SpawnManager(rng=random.Random(123))
    params_mixed = DifficultyParams(aggressive_ratio=0.5)
    aggressive_count_mixed = 0
    iterations = 200
    for _ in range(iterations):
        archetype = manager_mixed._select_archetype(params_mixed)
        if archetype == EnemyArchetype.AGGRESSIVE:
            aggressive_count_mixed += 1

    # Allow 20% tolerance for statistical variance
    expected = iterations * 0.5
    tolerance = iterations * 0.2
    assert (
        abs(aggressive_count_mixed - expected) <= tolerance
    ), f"Expected ~{expected} AGGRESSIVE with aggressive_ratio=0.5, got {aggressive_count_mixed}"


def test_reset_enemy_spawning_resets_timer() -> None:
    """Reset enemy spawning resets timer to zero."""
    manager = SpawnManager(rng=random.Random(42))
    params = DifficultyParams(
        enemy_spawn_enabled=True,
        enemy_count_max=5,
        enemy_spawn_interval=5.0,
        aggressive_ratio=0.3,
    )

    # Advance timer partway
    manager.update_enemy_spawning(
        dt=3.0,
        current_enemy_count=0,
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )

    # Reset timer
    manager.reset_enemy_spawning()

    # After reset, should not spawn immediately with small delta
    enemies = manager.update_enemy_spawning(
        dt=1.0,
        current_enemy_count=0,
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )
    assert len(enemies) == 0, "Timer should be reset, no spawn with dt=1.0"

    # But should spawn after full interval
    enemies = manager.update_enemy_spawning(
        dt=4.5,
        current_enemy_count=0,
        difficulty_params=params,
        screen_width=1280.0,
        screen_height=960.0,
    )
    assert len(enemies) == 1, "Should spawn after full interval post-reset"


def test_spawn_manager_integration_30_seconds() -> None:
    """Simulate 30s of spawning, verify count and archetype validity."""
    manager = SpawnManager(rng=random.Random(42))
    params = DifficultyParams(
        enemy_spawn_enabled=True,
        enemy_count_max=5,
        enemy_spawn_interval=3.0,
        aggressive_ratio=0.4,
        enemy_aggression=0.6,
    )

    total_spawned = 0
    current_count = 0
    dt_step = 1.0 / 60.0  # 60 FPS
    total_time = 0.0
    target_time = 30.0

    while total_time < target_time:
        enemies = manager.update_enemy_spawning(
            dt=dt_step,
            current_enemy_count=current_count,
            difficulty_params=params,
            screen_width=1280.0,
            screen_height=960.0,
        )

        if enemies:
            total_spawned += len(enemies)
            current_count += len(enemies)
            enemy = enemies[0]
            # Verify valid archetype
            assert enemy.archetype in [EnemyArchetype.BASIC, EnemyArchetype.AGGRESSIVE]
            # Verify has velocity
            assert enemy.velocity_x != 0.0 or enemy.velocity_y != 0.0

        # Simulate enemy death randomly to test continued spawning
        if current_count > 0 and total_time % 5.0 < dt_step:
            current_count -= 1

        total_time += dt_step

    # Over 30 seconds with 3s interval, expect roughly 10 spawn attempts
    # Given cap of 5 and simulated deaths, should have spawned at least 5-10 enemies
    assert (
        total_spawned >= 5
    ), f"Expected at least 5 spawns over 30s, got {total_spawned}"
    assert (
        total_spawned <= 15
    ), f"Expected at most 15 spawns over 30s, got {total_spawned}"
