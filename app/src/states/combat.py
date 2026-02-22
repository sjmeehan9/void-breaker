"""Combat phase state with full Phase 2 gameplay orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

import arcade
from asterax.app.src.config.difficulty_tables import get_difficulty_params
from asterax.app.src.config.game_config import (
    COLLISION_CONFIG,
    GAME_CONFIG,
    PHYSICS_CONFIG,
)
from asterax.app.src.config.game_config import GameState as RunGameState
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.managers.currency_manager import CurrencyManager
from asterax.app.src.managers.entity_manager import EntityManager
from asterax.app.src.managers.score_manager import ScoreManager
from asterax.app.src.managers.spawn_manager import SpawnManager
from asterax.app.src.physics.collisions import CollisionSystem
from asterax.app.src.physics.engine import PhysicsEngine
from asterax.app.src.rendering.hud import HUDRenderer
from asterax.app.src.rendering.particle_system import ParticleSystem
from asterax.app.src.states.base_state import BaseState

if TYPE_CHECKING:
    from asterax.app.src.persistence.persistence_manager import PersistenceManager
    from asterax.app.src.states.state_machine import StateMachine

PHYSICS_DT: Final[float] = GAME_CONFIG.physics_dt
MAX_FRAME_TIME: Final[float] = GAME_CONFIG.max_frame_time


class CombatPhaseState(BaseState):
    """Combat phase with level progression, collisions, and game-over transitions."""

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialize combat-phase manager references and run state."""
        super().__init__(state_machine)
        self.entity_manager = EntityManager()
        self.physics_engine: PhysicsEngine | None = None
        self.collision_system = CollisionSystem(
            collision_damage=COLLISION_CONFIG.ship_asteroid_damage
        )
        self.spawn_manager = SpawnManager()
        self.score_manager = ScoreManager()
        self.currency_manager = CurrencyManager()
        self.particle_system = ParticleSystem(self.entity_manager.particles)
        self.hud: HUDRenderer | None = None
        self.game_state = RunGameState()
        self.current_level = 1
        self.accumulator = 0.0
        self._game_over_triggered = False

    @property
    def player_ship(self) -> PlayerShip:
        """Return the active player ship for state-managed systems."""
        player = self.entity_manager.player_ship
        if player is None:
            raise RuntimeError("Player ship is not initialized")
        return player

    def on_enter(self) -> None:
        """Initialize combat entities, managers, HUD, and first level asteroids."""
        window = arcade.get_window()
        ship_sprite_path = (
            Path(__file__).resolve().parents[3] / "assets" / "sprites" / "ship.png"
        )
        ship = PlayerShip(
            sprite_path=ship_sprite_path,
            center_x=window.width / 2,
            center_y=window.height / 2,
            physics_config=PHYSICS_CONFIG,
        )
        self.entity_manager.player_ship = ship
        self.physics_engine = PhysicsEngine(self.entity_manager, PHYSICS_CONFIG)
        self.hud = HUDRenderer(window.width, window.height)
        self.current_level = 1
        self.accumulator = 0.0
        self._game_over_triggered = False
        self.score_manager.reset()
        self.currency_manager.reset()
        self.entity_manager.clear_projectiles()
        self.entity_manager.currency_pickups.clear()
        self.entity_manager.asteroids.clear()

        for asteroid in self.spawn_manager.spawn_level_asteroids(
            level=self.current_level,
            player_position=(ship.center_x, ship.center_y),
            screen_width=window.width,
            screen_height=window.height,
        ):
            self.entity_manager.asteroids.append(asteroid)
        self._sync_state_for_hud()

    def on_update(self, delta_time: float) -> None:
        """Advance combat simulation with a fixed-timestep accumulator."""
        if self.physics_engine is None:
            return

        frame_time = min(delta_time, MAX_FRAME_TIME)
        self.accumulator += frame_time
        while self.accumulator >= PHYSICS_DT:
            self._physics_step(PHYSICS_DT)
            self.accumulator -= PHYSICS_DT

    def _physics_step(self, dt: float) -> None:
        """Run one deterministic combat simulation step."""
        if self.physics_engine is None:
            return

        window = arcade.get_window()
        self.physics_engine.update(
            dt=dt,
            keys_held=window.input_manager.keys_held,
            input_manager=window.input_manager,
            width=window.width,
            height=window.height,
        )
        self.collision_system.check_all(
            entity_manager=self.entity_manager,
            game_state=self.game_state,
            spawn_manager=self.spawn_manager,
            score_manager=self.score_manager,
            screen_width=window.width,
            screen_height=window.height,
            currency_manager=self.currency_manager,
            audio_manager=window.audio_manager,
            particle_system=self.particle_system,
        )
        self.particle_system.update(dt)
        self._check_level_clear()
        if self.player_ship.shields <= 0.0:
            self._trigger_game_over(window.persistence)
            return
        self._sync_state_for_hud()

    def _sync_state_for_hud(self) -> None:
        """Refresh derived state values consumed by HUD and transitions."""
        self.game_state.current_level = self.current_level
        self.game_state.score = self.score_manager.score
        self.game_state.shields = self.player_ship.shields
        self.game_state.max_shields = self.player_ship.max_shields
        self.game_state.currency = self.currency_manager.get_balance()
        if self.hud is not None:
            self.hud.update_combat_values(
                score=self.game_state.score,
                level=self.current_level,
                shields=self.game_state.shields,
                max_shields=self.game_state.max_shields,
                credits=self.game_state.currency,
            )

    def _check_level_clear(self) -> None:
        """Advance to the next level when all asteroids are cleared."""
        if len(self.entity_manager.asteroids) == 0:
            self._advance_level()

    def _advance_level(self) -> None:
        """Increment level and spawn next-wave asteroids with updated difficulty."""
        window = arcade.get_window()
        self.current_level += 1
        self.entity_manager.clear_projectiles()
        self.entity_manager.currency_pickups.clear()
        ship = self.player_ship
        ship.center_x = window.width / 2
        ship.center_y = window.height / 2
        ship.velocity_x = 0.0
        ship.velocity_y = 0.0

        params = get_difficulty_params(self.current_level)
        for asteroid in self.spawn_manager.spawn_level_asteroids(
            level=self.current_level,
            player_position=(ship.center_x, ship.center_y),
            screen_width=window.width,
            screen_height=window.height,
        ):
            asteroid.velocity_x = max(
                -params.asteroid_speed_max,
                min(params.asteroid_speed_max, asteroid.velocity_x),
            )
            asteroid.velocity_y = max(
                -params.asteroid_speed_max,
                min(params.asteroid_speed_max, asteroid.velocity_y),
            )
            self.entity_manager.asteroids.append(asteroid)
        window.audio_manager.play("level_clear")
        self._sync_state_for_hud()

    def _trigger_game_over(self, persistence: PersistenceManager) -> None:
        """Transition to GameOver with run statistics snapshot."""
        if self._game_over_triggered:
            return
        self._game_over_triggered = True
        run_stats = {
            "score": self.score_manager.score,
            "level_reached": self.current_level,
            "currency_collected": self.currency_manager.total_earned,
            "currency_spent": self.currency_manager.total_spent,
            "currency_balance": self.currency_manager.get_balance(),
            "asteroids_destroyed": self.game_state.run_stats.asteroids_destroyed,
            "enemies_destroyed": self.game_state.run_stats.enemies_destroyed,
        }
        from asterax.app.src.states.game_over import GameOverState

        self.state_machine.switch_state(
            GameOverState(
                self.state_machine,
                run_stats=run_stats,
                persistence=persistence,
            )
        )

    def on_draw(self) -> None:
        """Draw combat scene entities, particles, and HUD."""
        self.entity_manager.draw()
        self.particle_system.draw()
        if self.hud is not None:
            self.hud.draw()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle combat-specific key transitions like pause or forced game-over."""
        del modifiers

        from asterax.app.src.states.pause import PauseState

        if key == arcade.key.ESCAPE:
            self.state_machine.push_state(PauseState(self.state_machine))
        elif key == arcade.key.G:
            window = arcade.get_window()
            self.player_ship.shields = 0.0
            self._trigger_game_over(window.persistence)
