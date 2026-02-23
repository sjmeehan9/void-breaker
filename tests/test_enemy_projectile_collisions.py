"""Phase 3.3 tests for enemy projectiles and expanded collision pairs."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import arcade
from asterax.app.src.config.enemy_config import EnemyArchetype, get_basic_config
from asterax.app.src.config.game_config import PhysicsConfig
from asterax.app.src.entities.enemy_ship import EnemyShip
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.entities.projectile import Projectile, ProjectileOwner
from asterax.app.src.physics.collisions import CollisionSystem
from asterax.app.src.states.combat import CombatPhaseState

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites"


class DummyEntityManager:
    """Minimal entity manager exposing collections used by collision methods."""

    def __init__(self, player_ship: PlayerShip) -> None:
        self.player_ship = player_ship
        self.player_projectiles = arcade.SpriteList()
        self.enemy_projectiles = arcade.SpriteList()
        self.enemies = arcade.SpriteList()


class _FiringEnemy(arcade.Sprite):
    """Test enemy sprite that emits a single configured projectile."""

    def __init__(self, projectile: Projectile) -> None:
        super().__init__(
            str(ASSETS_DIR / "enemy_basic.png"),
            center_x=projectile.center_x,
            center_y=projectile.center_y,
        )
        self._projectile = projectile
        self._fired = False

    def update_ai(self, dt: float, player_position: tuple[float, float]) -> None:
        """Satisfy combat update protocol with no movement."""
        del dt, player_position

    def try_fire(
        self,
        dt: float,
        player_position: tuple[float, float],
        player_velocity: tuple[float, float],
    ) -> Projectile | None:
        """Return one projectile the first time this method is called."""
        del dt, player_position, player_velocity
        if self._fired:
            return None
        self._fired = True
        return self._projectile

    def take_damage(self, amount: float) -> bool:
        """Satisfy collision response protocol for tests."""
        del amount
        return False

    def on_destroyed(self) -> dict[str, int]:
        """Return reward payload matching enemy entity API."""
        return {"point_value": 0}


def _make_ship(center_x: float = 640.0, center_y: float = 480.0) -> PlayerShip:
    return PlayerShip(
        sprite_path=ASSETS_DIR / "ship.png",
        center_x=center_x,
        center_y=center_y,
        physics_config=PhysicsConfig(),
    )


def test_player_vs_enemy_projectiles_detects_wrap_ghost_collision() -> None:
    """Player should collide with enemy projectile across wrapped screen seam."""
    entity_manager = DummyEntityManager(_make_ship(center_x=4.0, center_y=300.0))
    projectile = Projectile(
        center_x=1278.0,
        center_y=300.0,
        angle=0.0,
        speed=0.0,
        max_range=600.0,
        damage=10.0,
        owner=ProjectileOwner.ENEMY,
    )
    entity_manager.enemy_projectiles.append(projectile)

    collisions = CollisionSystem().check_player_vs_enemy_projectiles(
        entity_manager=entity_manager,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert collisions == [(entity_manager.player_ship, projectile)]


def test_player_projectiles_vs_enemies_detects_collisions() -> None:
    """Player projectile should report collision pair with enemy ship."""
    entity_manager = DummyEntityManager(_make_ship())
    enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=get_basic_config(),
        center_x=200.0,
        center_y=200.0,
    )
    projectile = Projectile(
        center_x=200.0,
        center_y=200.0,
        angle=0.0,
        speed=0.0,
        max_range=600.0,
        damage=1.0,
    )
    entity_manager.enemies.append(enemy)
    entity_manager.player_projectiles.append(projectile)

    collisions = CollisionSystem().check_player_projectiles_vs_enemies(
        entity_manager=entity_manager,
        screen_width=1280.0,
        screen_height=960.0,
    )

    assert collisions == [(projectile, enemy)]


def test_combat_process_enemy_collisions_applies_damage_and_cleanup() -> None:
    """Combat collision processing should damage player and remove enemy/projectiles."""
    state = CombatPhaseState(state_machine=SimpleNamespace())
    ship = _make_ship(center_x=400.0, center_y=400.0)
    state.entity_manager.player_ship = ship

    enemy = EnemyShip(
        archetype=EnemyArchetype.BASIC,
        config=get_basic_config(),
        center_x=400.0,
        center_y=400.0,
    )
    enemy.health = state.collision_system.collision_damage
    player_projectile = Projectile(
        center_x=400.0,
        center_y=400.0,
        angle=0.0,
        speed=0.0,
        max_range=600.0,
        damage=enemy.health,
    )
    enemy_projectile = Projectile(
        center_x=400.0,
        center_y=400.0,
        angle=0.0,
        speed=0.0,
        max_range=600.0,
        damage=12.0,
        owner=ProjectileOwner.ENEMY,
    )
    state.entity_manager.enemies.append(enemy)
    state.entity_manager.player_projectiles.append(player_projectile)
    state.entity_manager.enemy_projectiles.append(enemy_projectile)

    starting_shields = ship.shields
    state._process_enemy_collisions(screen_width=1280.0, screen_height=960.0)

    assert ship.shields < starting_shields
    assert enemy not in state.entity_manager.enemies
    assert player_projectile not in state.entity_manager.player_projectiles
    assert enemy_projectile not in state.entity_manager.enemy_projectiles
    assert state.score_manager.score == enemy.point_value


def test_combat_update_enemies_spawns_then_expires_enemy_projectiles() -> None:
    """Enemy update should append fired projectiles and remove expired projectiles."""
    state = CombatPhaseState(state_machine=SimpleNamespace())
    state.entity_manager.player_ship = _make_ship(center_x=200.0, center_y=250.0)
    fired_projectile = Projectile(
        center_x=200.0,
        center_y=250.0,
        angle=0.0,
        speed=100.0,
        max_range=5.0,
        damage=8.0,
        owner=ProjectileOwner.ENEMY,
    )
    state.entity_manager.enemies.append(_FiringEnemy(fired_projectile))

    state._update_enemies(dt=0.01, screen_width=1280.0, screen_height=960.0)
    assert fired_projectile in state.entity_manager.enemy_projectiles

    state._update_enemies(dt=0.2, screen_width=1280.0, screen_height=960.0)
    assert fired_projectile not in state.entity_manager.enemy_projectiles


def test_apply_player_damage_triggers_hit_feedback_and_invulnerability(
    monkeypatch,
) -> None:
    """Applying damage should play hit audio and block immediate follow-up damage."""
    state = CombatPhaseState(state_machine=SimpleNamespace())
    ship = _make_ship()
    state.entity_manager.player_ship = ship
    audio_calls: list[str] = []
    monkeypatch.setattr(
        arcade,
        "get_window",
        lambda: SimpleNamespace(audio_manager=SimpleNamespace(play=audio_calls.append)),
    )

    starting_shields = ship.shields
    state._apply_player_damage(ship, 10.0)
    shields_after_hit = ship.shields
    state._apply_player_damage(ship, 10.0)

    assert shields_after_hit < starting_shields
    assert ship.shields == shields_after_hit
    assert ship.is_invulnerable is True
    assert audio_calls == ["player_hit"]
