"""Focused tests for Phase 3.7 buff pickup entities and manager logic."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import arcade
from asterax.app.src.config.enemy_config import EnemyArchetype, get_basic_config
from asterax.app.src.config.game_config import PhysicsConfig
from asterax.app.src.entities.buff_pickup import BuffPickup, BuffType
from asterax.app.src.entities.enemy_ship import EnemyShip
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.managers.buff_manager import BuffManager
from asterax.app.src.states.combat import CombatPhaseState

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites"


def _make_ship(center_x: float = 640.0, center_y: float = 480.0) -> PlayerShip:
    return PlayerShip(
        sprite_path=ASSETS_DIR / "ship.png",
        center_x=center_x,
        center_y=center_y,
        physics_config=PhysicsConfig(),
    )


def test_buff_pickup_creation_supports_all_types() -> None:
    """BuffPickup should preserve type-specific metadata for each buff type."""
    for buff_type in BuffType:
        pickup = BuffPickup(
            buff_type=buff_type,
            magnitude=1.0,
            duration=8.0,
            center_x=100.0,
            center_y=120.0,
        )
        assert pickup.buff_type is buff_type
        assert pickup.magnitude == 1.0


def test_buff_pickup_lifetime_expiry_removes_from_sprite_list() -> None:
    """Expired buff pickups should remove themselves from parent sprite lists."""
    pickup = BuffPickup(
        buff_type=BuffType.HEAL,
        magnitude=0.25,
        duration=0.0,
        center_x=100.0,
        center_y=120.0,
        lifetime=0.05,
    )
    pickups = arcade.SpriteList()
    pickups.append(pickup)

    pickup.update(0.1)

    assert pickup not in pickups


def test_buff_manager_apply_heal_restores_shields_up_to_maximum() -> None:
    """HEAL buffs should restore shields and clamp at max shields."""
    ship = _make_ship()
    ship.shields = 80.0
    manager = BuffManager()

    manager.apply_buff(BuffType.HEAL, magnitude=0.25, duration=0.0, ship=ship)

    assert ship.shields == ship.max_shields
    assert manager.get_active_buffs() == []


def test_buff_manager_damage_boost_applies_and_expires() -> None:
    """Damage boost should modify effective damage and restore on expiry."""
    ship = _make_ship()
    manager = BuffManager()

    manager.apply_buff(BuffType.DAMAGE_BOOST, magnitude=1.5, duration=8.0, ship=ship)
    assert ship.effective_damage == ship.physics_config.base_damage * 1.5

    manager.update(8.1, ship)

    assert ship.effective_damage == ship.physics_config.base_damage


def test_buff_manager_speed_boost_applies_and_expires() -> None:
    """Speed boost should modify effective thrust and restore on expiry."""
    ship = _make_ship()
    manager = BuffManager()

    manager.apply_buff(BuffType.SPEED_BOOST, magnitude=1.4, duration=8.0, ship=ship)
    assert ship.effective_thrust == ship.physics_config.base_thrust * 1.4

    manager.update(8.1, ship)

    assert ship.effective_thrust == ship.physics_config.base_thrust


def test_same_type_buff_refreshes_duration_without_stacking() -> None:
    """Reapplying one buff type should refresh timer while keeping one active entry."""
    ship = _make_ship()
    manager = BuffManager()

    manager.apply_buff(BuffType.DAMAGE_BOOST, magnitude=1.5, duration=8.0, ship=ship)
    manager.update(3.0, ship)
    manager.apply_buff(BuffType.DAMAGE_BOOST, magnitude=1.5, duration=8.0, ship=ship)
    active = manager.get_active_buffs()

    assert len(active) == 1
    assert active[0][0] is BuffType.DAMAGE_BOOST
    assert active[0][1] == 8.0


def test_buff_manager_clear_all_removes_active_buffs() -> None:
    """clear_all should reset all modified ship stats and empty active buffs."""
    ship = _make_ship()
    manager = BuffManager()
    manager.apply_buff(BuffType.DAMAGE_BOOST, magnitude=1.5, duration=8.0, ship=ship)
    manager.apply_buff(BuffType.SPEED_BOOST, magnitude=1.4, duration=8.0, ship=ship)

    manager.clear_all(ship)

    assert manager.get_active_buffs() == []
    assert ship.effective_damage == ship.physics_config.base_damage
    assert ship.effective_thrust == ship.physics_config.base_thrust


def test_enemy_buff_drop_and_collection_applies_effect(monkeypatch) -> None:
    """Enemy buff drops should spawn pickups and apply effects on collection."""
    state = CombatPhaseState(state_machine=SimpleNamespace())
    ship = _make_ship(center_x=400.0, center_y=300.0)
    state.entity_manager.player_ship = ship
    enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=get_basic_config(),
        center_x=400.0,
        center_y=300.0,
    )

    monkeypatch.setattr("asterax.app.src.states.combat.random.random", lambda: 0.0)
    monkeypatch.setattr(
        "asterax.app.src.states.combat.random.choices",
        lambda population, weights, k: [BuffType.DAMAGE_BOOST],
    )
    state._maybe_spawn_enemy_buff(enemy, buff_drop_chance=1.0)

    assert len(state.entity_manager.buff_pickups) == 1

    state._process_enemy_collisions(screen_width=1280.0, screen_height=960.0)

    assert len(state.entity_manager.buff_pickups) == 0
    assert ship.effective_damage == ship.physics_config.base_damage * 1.5
