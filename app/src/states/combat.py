"""Combat phase state with full Phase 2 gameplay orchestration."""

from __future__ import annotations

import json
import math
import os
import random
import statistics
import time
from pathlib import Path
from typing import TYPE_CHECKING, Final

import arcade
from asterax.app.src.config.difficulty_tables import (
    DIFFICULTY_PRESET_MULTIPLIERS,
    DifficultyMultipliers,
    DifficultyPreset,
    get_difficulty_params,
    parse_difficulty_preset,
)
from asterax.app.src.config.enemy_config import EnemyArchetype as EnemyKind
from asterax.app.src.config.enemy_config import (
    get_aggressive_config,
    get_basic_config,
)
from asterax.app.src.config.game_config import (
    COLLISION_CONFIG,
    GAME_CONFIG,
    PHYSICS_CONFIG,
    AsteroidSize,
    DifficultyParams,
)
from asterax.app.src.config.game_config import GameState as RunGameState
from asterax.app.src.config.game_config import (
    RunStats,
    ShipState,
)
from asterax.app.src.entities.asteroid import Asteroid
from asterax.app.src.entities.buff_pickup import BuffPickup, BuffType
from asterax.app.src.entities.enemy_ship import EnemyShip
from asterax.app.src.entities.pickups import CurrencyPickup
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.entities.projectile import Projectile, ProjectileOwner
from asterax.app.src.managers.buff_manager import BuffManager
from asterax.app.src.managers.currency_manager import CurrencyManager
from asterax.app.src.managers.difficulty_scaler import DifficultyScaler
from asterax.app.src.managers.entity_manager import EntityManager
from asterax.app.src.managers.score_manager import ScoreManager
from asterax.app.src.managers.spawn_manager import SpawnManager
from asterax.app.src.physics.collisions import CollisionSystem
from asterax.app.src.physics.engine import PhysicsEngine
from asterax.app.src.physics.wrap import wrap_entity
from asterax.app.src.rendering.damage_effects import DamageEffects
from asterax.app.src.rendering.hud import HUDRenderer
from asterax.app.src.rendering.particle_system import ParticleSystem
from asterax.app.src.rendering.transitions import (
    TransitionEffect,
    apply_colorblind_palette_to_combat,
)
from asterax.app.src.states.base_state import BaseState
from asterax.app.src.utils.paths import get_asset_path

if TYPE_CHECKING:
    from asterax.app.src.persistence.persistence_manager import PersistenceManager
    from asterax.app.src.states.state_machine import StateMachine

PHYSICS_DT: Final[float] = GAME_CONFIG.physics_dt
MAX_FRAME_TIME: Final[float] = GAME_CONFIG.max_frame_time
BUFF_PICKUP_SOUND_NAME: Final[str] = (
    "pickup_buff"
    if get_asset_path("sounds", "pickup_buff.wav").exists()
    else "pickup_currency"
)
PERF_TARGET_COUNTS: Final[dict[str, int]] = {
    "asteroids": 100,
    "enemies": 10,
    "player_projectiles": 15,
    "enemy_projectiles": 20,
    "pickups": 40,
    "particles": 300,
}


class CombatPhaseState(BaseState):
    """Combat phase with level progression, collisions, and game-over transitions."""

    def __init__(
        self,
        state_machine: StateMachine,
        initial_level: int = 1,
        initial_score: int = 0,
        initial_currency: int = 0,
        initial_run_stats: RunStats | None = None,
        is_practice: bool = False,
        practice_asteroids_only: bool = False,
        practice_infinite_shields: bool = False,
        practice_reduced_count: bool = False,
        practice_params_override: DifficultyParams | None = None,
        perf_stress_mode: bool = False,
        perf_duration_seconds: float = 60.0,
        perf_output_path: str | None = None,
        perf_seed: int = 1337,
    ) -> None:
        """Initialize combat-phase manager references and run state."""
        super().__init__(state_machine)
        self.entity_manager = EntityManager()
        self.physics_engine: PhysicsEngine | None = None
        self.collision_system = CollisionSystem(
            collision_damage=COLLISION_CONFIG.ship_asteroid_damage
        )
        self.spawn_manager = SpawnManager()
        self.difficulty_scaler = DifficultyScaler()
        self.score_manager = ScoreManager()
        self.game_state = RunGameState()
        self.currency_manager = CurrencyManager(self.game_state)
        self.buff_manager = BuffManager()
        self.particle_system = ParticleSystem(self.entity_manager.particles)
        self.damage_effects = DamageEffects()
        self.hud: HUDRenderer | None = None
        self.current_level = max(1, initial_level)
        self._initial_score = max(0, initial_score)
        self._initial_currency = max(0, initial_currency)
        self._initial_run_stats = initial_run_stats
        self.accumulator = 0.0
        self._game_over_triggered = False
        self._game_over_delay_remaining = 0.0
        self._last_player_projectile_count = 0
        self._transition_effect: TransitionEffect | None = None
        self._difficulty_preset: DifficultyPreset = DifficultyPreset.CLASSIC
        self._current_difficulty_params: DifficultyParams | None = None
        self._damage_received_multiplier: float = 1.0
        self._is_practice = bool(is_practice)
        self._practice_asteroids_only = bool(practice_asteroids_only)
        self._practice_infinite_shields = bool(practice_infinite_shields)
        self._practice_reduced_count = bool(practice_reduced_count)
        self._practice_params_override = practice_params_override
        self._perf_stress_mode = bool(perf_stress_mode)
        self._perf_duration_seconds = max(1.0, float(perf_duration_seconds))
        self._perf_output_path = perf_output_path
        self._perf_seed = int(perf_seed)
        self._perf_elapsed_seconds = 0.0
        self._perf_frame_times_ms: list[float] = []
        self._perf_finished = False
        self._perf_started_at_monotonic = 0.0

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
        ship_sprite_path = get_asset_path("sprites", "ship.png")
        ship = PlayerShip(
            sprite_path=ship_sprite_path,
            center_x=window.width / 2,
            center_y=window.height / 2,
            physics_config=PHYSICS_CONFIG,
        )
        self.entity_manager.player_ship = ship
        self.physics_engine = PhysicsEngine(self.entity_manager, PHYSICS_CONFIG)
        self.hud = HUDRenderer(window.width, window.height)
        self.current_level = max(1, self.current_level)
        self.accumulator = 0.0
        self._game_over_triggered = False
        self._game_over_delay_remaining = 0.0
        self._last_player_projectile_count = 0
        self.score_manager.reset()
        self.currency_manager.reset()
        self.game_state.is_practice = self._is_practice
        self.score_manager.score = self._initial_score
        if self._initial_currency > 0:
            self.currency_manager.earn(self._initial_currency)
        if self._initial_run_stats is not None:
            self.game_state.run_stats = self._initial_run_stats
        self.entity_manager.clear_projectiles()
        self.entity_manager.clear_enemies()
        self.entity_manager.currency_pickups.clear()
        self.entity_manager.buff_pickups.clear()
        self.entity_manager.asteroids.clear()
        self.buff_manager.clear_all(ship)
        if self._practice_infinite_shields:
            ship.shields = ship.max_shields
        self._difficulty_preset = self._resolve_difficulty_preset()
        params = self._practice_params_override or self._params_for_level(
            self.current_level
        )
        self._practice_params_override = None
        self._apply_runtime_difficulty(params)

        for asteroid in self.spawn_manager.spawn_level_asteroids(
            level=self.current_level,
            player_position=(ship.center_x, ship.center_y),
            screen_width=window.width,
            screen_height=window.height,
            difficulty_params=params,
        ):
            self.entity_manager.asteroids.append(asteroid)
        self.spawn_manager.reset_enemy_spawning()
        self._transition_effect = TransitionEffect(window.width, window.height)
        if self.current_level > 1:
            self._transition_effect.start_level_transition(self.current_level)
        self._apply_visual_settings()
        if self._perf_stress_mode:
            self._setup_performance_stress_scene(window.width, window.height)
            self._transition_effect = None
            self._perf_started_at_monotonic = time.monotonic()
        self._sync_state_for_hud()

    def on_update(self, delta_time: float) -> None:
        """Advance combat simulation with a fixed-timestep accumulator."""
        if self._perf_stress_mode and self._perf_finished:
            return
        if self.physics_engine is None:
            return

        if self._transition_effect is not None and self._transition_effect.is_active:
            self._transition_effect.update(delta_time)
            self._apply_visual_settings()
            return

        frame_time = min(delta_time, MAX_FRAME_TIME)
        if self._perf_stress_mode:
            self._perf_frame_times_ms.append(max(0.0, frame_time) * 1000.0)
            self._perf_elapsed_seconds += frame_time
        self.accumulator += frame_time
        while self.accumulator >= PHYSICS_DT:
            self._physics_step(PHYSICS_DT)
            self.accumulator -= PHYSICS_DT
        if (
            self._perf_stress_mode
            and self._perf_elapsed_seconds >= self._perf_duration_seconds
        ):
            self._finish_performance_run()

    def _physics_step(self, dt: float) -> None:
        """Run one deterministic combat simulation step."""
        if self.physics_engine is None:
            return
        if self._perf_stress_mode:
            self._physics_step_performance(dt)
            self._sync_state_for_hud()
            return

        window = arcade.get_window()
        shields_before_collisions = self.player_ship.shields
        self.physics_engine.update(
            dt=dt,
            keys_held=window.input_manager.keys_held,
            input_manager=window.input_manager,
            width=window.width,
            height=window.height,
        )
        self._emit_thrust_particles()
        self._process_player_fire_sound()
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
        if self.player_ship.shields < shields_before_collisions:
            self.player_ship.trigger_damage_flash_tint()
            self.damage_effects.trigger_invulnerability(
                self.player_ship, GAME_CONFIG.invulnerability_duration
            )
            self.particle_system.emit_damage_flash(
                self.player_ship.center_x,
                self.player_ship.center_y,
            )
            self._trigger_screen_shake()
        self._spawn_enemies(
            dt=dt, screen_width=window.width, screen_height=window.height
        )
        self._update_enemies(
            dt=dt,
            screen_width=window.width,
            screen_height=window.height,
        )
        self._process_enemy_collisions(
            screen_width=window.width,
            screen_height=window.height,
        )
        for buff_pickup in list(self.entity_manager.buff_pickups):
            buff_pickup.update(dt)
        self.buff_manager.update(dt, self.player_ship)
        self.player_ship.update_invulnerability(dt)
        self.damage_effects.update(dt)
        self.particle_system.update(dt)
        self._apply_visual_settings()
        self._check_level_clear()
        if self.player_ship.shields <= 0.0:
            if self._is_practice:
                self._respawn_practice_ship()
                self._sync_state_for_hud()
                return
            if self._game_over_delay_remaining <= 0.0:
                self._game_over_delay_remaining = 0.8
                self.damage_effects.trigger_destruction_sequence(
                    (self.player_ship.center_x, self.player_ship.center_y),
                    self.entity_manager.particles,
                )
            self._game_over_delay_remaining = max(
                0.0, self._game_over_delay_remaining - dt
            )
            if self._game_over_delay_remaining <= 0.0:
                self._trigger_game_over(window.persistence)
            return
        self._sync_state_for_hud()

    def _sync_state_for_hud(self) -> None:
        """Refresh derived state values consumed by HUD and transitions."""
        self.game_state.current_level = self.current_level
        self.game_state.score = self.score_manager.score
        self.game_state.shields = self.player_ship.shields
        self.game_state.max_shields = self.player_ship.max_shields
        if self.hud is not None:
            self.hud.update_combat_values(
                score=self.game_state.score,
                level=self.current_level,
                shields=self.game_state.shields,
                max_shields=self.game_state.max_shields,
                credits=self.game_state.currency,
                is_practice=self._is_practice,
            )

    def _check_level_clear(self) -> None:
        """Transition to shop when all asteroids are cleared."""
        if len(self.entity_manager.asteroids) == 0:
            if self._is_practice:
                self._advance_level()
                return
            self._transition_to_shop()

    def _transition_to_shop(self) -> None:
        """Switch into ShopPhase with snapshots of current run and ship state."""
        ship = self.player_ship
        self._sync_state_for_hud()
        self._play_level_clear_sound()
        from asterax.app.src.states.shop import ShopPhaseState

        self.state_machine.switch_state(
            ShopPhaseState(
                self.state_machine,
                game_state=self.game_state,
                ship_state=ShipState(
                    position=(ship.center_x, ship.center_y),
                    velocity=(ship.velocity_x, ship.velocity_y),
                    angle=ship.angle,
                ),
            )
        )

    def _advance_level(self) -> None:
        """Increment level and spawn next-wave asteroids with updated difficulty."""
        window = arcade.get_window()
        self.current_level += 1
        self.entity_manager.clear_projectiles()
        self.entity_manager.clear_enemies()
        self.entity_manager.currency_pickups.clear()
        self.entity_manager.buff_pickups.clear()
        ship = self.player_ship
        ship.center_x = window.width / 2
        ship.center_y = window.height / 2
        ship.velocity_x = 0.0
        ship.velocity_y = 0.0

        params = self._params_for_level(self.current_level)
        self._apply_runtime_difficulty(params)
        for asteroid in self.spawn_manager.spawn_level_asteroids(
            level=self.current_level,
            player_position=(ship.center_x, ship.center_y),
            screen_width=window.width,
            screen_height=window.height,
            difficulty_params=params,
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
        self.spawn_manager.reset_enemy_spawning()
        if hasattr(window.audio_manager, "play_level_clear"):
            window.audio_manager.play_level_clear()
        else:
            window.audio_manager.play("level_clear")
        self._sync_state_for_hud()

    def _trigger_game_over(self, persistence: PersistenceManager) -> None:
        """Transition to GameOver with run statistics snapshot."""
        if self._game_over_triggered:
            return
        self._game_over_triggered = True
        if self.entity_manager.player_ship is not None:
            self.buff_manager.clear_all(self.player_ship)
        run_stats = {
            "score": self.score_manager.score,
            "level_reached": self.current_level,
            "currency_collected": self.currency_manager.total_earned,
            "currency_spent": self.currency_manager.total_spent,
            "currency_balance": self.currency_manager.get_balance(),
            "asteroids_destroyed": self.game_state.run_stats.asteroids_destroyed,
            "enemies_destroyed": self.game_state.run_stats.enemies_destroyed,
            "insurance_tier": self.game_state.insurance.tier.value,
        }
        from asterax.app.src.states.game_over import GameOverState

        self.state_machine.switch_state(
            GameOverState(
                self.state_machine,
                run_stats=run_stats,
                persistence=persistence,
                is_practice=self._is_practice,
            )
        )

    def _spawn_enemies(
        self,
        dt: float,
        screen_width: float,
        screen_height: float,
    ) -> None:
        """Spawn new enemies at interval if enabled and under count cap."""
        difficulty_params = self._current_difficulty_params
        if difficulty_params is None:
            difficulty_params = self._params_for_level(self.current_level)
            self._apply_runtime_difficulty(difficulty_params)
        new_enemies = self.spawn_manager.update_enemy_spawning(
            dt=dt,
            current_enemy_count=len(self.entity_manager.enemies),
            difficulty_params=difficulty_params,
            screen_width=screen_width,
            screen_height=screen_height,
        )
        for enemy in new_enemies:
            self.entity_manager.enemies.append(enemy)

    def _update_enemies(
        self,
        dt: float,
        screen_width: float,
        screen_height: float,
    ) -> None:
        """Advance enemy movement/firing and maintain enemy projectile lifetimes."""
        player = self.player_ship
        player_position = (player.center_x, player.center_y)
        player_velocity = (player.velocity_x, player.velocity_y)

        for enemy in list(self.entity_manager.enemies):
            enemy.update_ai(dt=dt, player_position=player_position)
            wrap_entity(enemy, screen_width, screen_height)
            projectile = enemy.try_fire(
                dt=dt,
                player_position=player_position,
                player_velocity=player_velocity,
            )
            if projectile is not None:
                self.entity_manager.enemy_projectiles.append(projectile)
                self._play_enemy_fire_sound()

        for projectile in list(self.entity_manager.enemy_projectiles):
            projectile.update(dt)
            wrap_entity(projectile, screen_width, screen_height)

    def _handle_enemy_destroyed(self, enemy: EnemyShip) -> None:
        """Apply score/stat updates and remove a destroyed enemy sprite."""
        rewards = enemy.on_destroyed()
        self.score_manager.score += int(rewards.get("point_value", 0))
        self.game_state.run_stats.enemies_destroyed += 1
        self._maybe_spawn_enemy_buff(enemy, float(rewards.get("buff_drop_chance", 0.0)))
        self.damage_effects.trigger_explosion(
            (enemy.center_x, enemy.center_y),
            "medium",
            self.entity_manager.particles,
        )
        self._play_enemy_explode_sound()
        enemy.kill()

    def _process_enemy_collisions(
        self,
        screen_width: float,
        screen_height: float,
    ) -> None:
        """Resolve enemy-related collisions after movement updates."""
        collision_pairs = self.collision_system.check_all_combat(
            entity_manager=self.entity_manager,
            screen_width=screen_width,
            screen_height=screen_height,
        )
        for player, enemy_projectile in collision_pairs["player_vs_enemy_projectiles"]:
            if enemy_projectile in self.entity_manager.enemy_projectiles:
                self._apply_player_damage(player, enemy_projectile.damage)
                enemy_projectile.kill()

        for projectile, enemy in collision_pairs["player_projectiles_vs_enemies"]:
            if (
                projectile not in self.entity_manager.player_projectiles
                or enemy not in self.entity_manager.enemies
            ):
                continue
            destroyed = enemy.take_damage(projectile.damage)
            projectile.kill()
            if destroyed:
                self._handle_enemy_destroyed(enemy)

        for player, enemy in collision_pairs["player_vs_enemies"]:
            if enemy not in self.entity_manager.enemies:
                continue
            self._apply_player_damage(player, self.collision_system.collision_damage)
            destroyed = enemy.take_damage(self.collision_system.collision_damage)
            if destroyed:
                self._handle_enemy_destroyed(enemy)
        for player, buff_pickup in collision_pairs["player_vs_buff_pickups"]:
            if buff_pickup not in self.entity_manager.buff_pickups:
                continue
            self.buff_manager.apply_buff(
                buff_type=buff_pickup.buff_type,
                magnitude=buff_pickup.magnitude,
                duration=buff_pickup.duration,
                ship=player,
            )
            self.particle_system.emit_sparkle(
                buff_pickup.center_x,
                buff_pickup.center_y,
            )
            buff_pickup.kill()
            self._play_buff_pickup_sound()

    def _apply_player_damage(self, player: PlayerShip, amount: float) -> None:
        """Apply player damage and trigger associated audiovisual feedback."""
        if self._practice_infinite_shields:
            player.shields = player.max_shields
            return
        if player.is_invulnerable:
            return
        took_damage = player.shields
        player.take_damage(amount * self._damage_received_multiplier)
        if player.shields < took_damage:
            player.trigger_damage_flash_tint()
            self.damage_effects.trigger_invulnerability(
                player, GAME_CONFIG.invulnerability_duration
            )
            self.particle_system.emit_damage_flash(
                player.center_x,
                player.center_y,
            )
            self._play_hit_sound()
            self._trigger_screen_shake()

    def _play_sound(self, sound_name: str) -> None:
        """Play a sound effect when a game window and audio manager are available."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        window.audio_manager.play(sound_name)

    def _play_level_clear_sound(self) -> None:
        """Play level-clear sound effect when available."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        if hasattr(window.audio_manager, "play_level_clear"):
            window.audio_manager.play_level_clear()
            return
        window.audio_manager.play("level_clear")

    def _play_hit_sound(self) -> None:
        """Play player-hit sound effect when available."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        if hasattr(window.audio_manager, "play_hit"):
            window.audio_manager.play_hit()
            return
        window.audio_manager.play("player_hit")

    def _play_enemy_explode_sound(self) -> None:
        """Play enemy-explosion sound effect when available."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        if hasattr(window.audio_manager, "play_enemy_explode"):
            window.audio_manager.play_enemy_explode()
            return
        window.audio_manager.play("enemy_explode")

    def _play_buff_pickup_sound(self) -> None:
        """Play buff pickup sound with fallback compatibility."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        if BUFF_PICKUP_SOUND_NAME == "pickup_buff":
            if hasattr(window.audio_manager, "play_pickup_buff"):
                window.audio_manager.play_pickup_buff()
            else:
                window.audio_manager.play("pickup_buff")
            return
        if hasattr(window.audio_manager, "play_pickup_currency"):
            window.audio_manager.play_pickup_currency()
            return
        window.audio_manager.play("pickup_currency")

    def _play_enemy_fire_sound(self) -> None:
        """Play enemy fire sound when an enemy projectile is emitted."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        if hasattr(window.audio_manager, "play_enemy_fire"):
            window.audio_manager.play_enemy_fire()
            return
        window.audio_manager.play("enemy_fire")

    def _emit_thrust_particles(self) -> None:
        """Emit thrust trail particles while thrust input is active."""
        window = arcade.get_window()
        input_manager = getattr(window, "input_manager", None)
        is_action_held = getattr(input_manager, "is_action_held", None)
        if not callable(is_action_held):
            return
        if not bool(is_action_held("thrust")):
            return
        ship = self.player_ship
        angle_radians = math.radians(90.0 - ship.angle)
        thrust_origin_x = ship.center_x - math.cos(angle_radians) * (ship.height / 2)
        thrust_origin_y = ship.center_y - math.sin(angle_radians) * (ship.height / 2)
        self.particle_system.emit_thrust(
            thrust_origin_x,
            thrust_origin_y,
            ship.angle,
        )

    def _process_player_fire_sound(self) -> None:
        """Play fire SFX exactly when a new player projectile is emitted."""
        current_count = len(self.entity_manager.player_projectiles)
        if current_count > self._last_player_projectile_count:
            try:
                window = arcade.get_window()
            except RuntimeError:
                return
            if hasattr(window.audio_manager, "play_fire"):
                window.audio_manager.play_fire()
            else:
                window.audio_manager.play("fire")
        self._last_player_projectile_count = current_count

    def _maybe_spawn_enemy_buff(
        self, enemy: EnemyShip, buff_drop_chance: float
    ) -> None:
        """Spawn a buff pickup from enemy destruction when drop chance roll succeeds."""
        if random.random() >= buff_drop_chance:
            return
        buff_type = random.choices(
            population=[BuffType.HEAL, BuffType.DAMAGE_BOOST, BuffType.SPEED_BOOST],
            weights=[0.4, 0.3, 0.3],
            k=1,
        )[0]
        magnitude, duration = self._buff_values(buff_type)
        self.entity_manager.buff_pickups.append(
            BuffPickup(
                buff_type=buff_type,
                magnitude=magnitude,
                duration=duration,
                center_x=enemy.center_x,
                center_y=enemy.center_y,
            )
        )

    def _buff_values(self, buff_type: BuffType) -> tuple[float, float]:
        """Return default magnitude and duration for each supported buff type."""
        if buff_type is BuffType.HEAL:
            return (0.25, 0.0)
        if buff_type is BuffType.DAMAGE_BOOST:
            return (1.5, 8.0)
        return (1.4, 8.0)

    def on_draw(self) -> None:
        """Draw combat scene entities, particles, and HUD."""
        self.entity_manager.draw()
        self.particle_system.draw()
        if self.hud is not None:
            self.hud.draw()
        if self._transition_effect is not None and self._transition_effect.is_active:
            self._transition_effect.draw()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle combat-specific key transitions like pause or forced game-over."""
        del modifiers

        from asterax.app.src.states.pause import PauseState

        if key == self._pause_key():
            self.state_machine.push_state(PauseState(self.state_machine))
        elif key == arcade.key.G:
            if self._is_practice:
                self._respawn_practice_ship()
                return
            window = arcade.get_window()
            self.player_ship.shields = 0.0
            self._trigger_game_over(window.persistence)

    def _pause_key(self) -> int:
        """Return current configured pause key binding.

        Returns:
            Key code for pause action with Escape fallback.
        """
        window = arcade.get_window()
        input_manager = getattr(window, "input_manager", None)
        get_binding = getattr(input_manager, "get_binding", None)
        if callable(get_binding):
            return int(get_binding("pause"))
        return arcade.key.ESCAPE

    def _apply_visual_settings(self) -> None:
        """Apply colorblind palette according to the active runtime settings."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        settings = getattr(window, "runtime_settings", None)
        if settings is None and hasattr(window, "persistence"):
            load_settings = getattr(window.persistence, "load_settings", None)
            if callable(load_settings):
                settings = load_settings()
        colorblind_enabled = bool(
            getattr(settings, "colorblind_mode", False)
            if settings is not None
            else False
        )
        apply_colorblind_palette_to_combat(self.entity_manager, colorblind_enabled)

    def _trigger_screen_shake(self) -> None:
        """Trigger window-level screen shake with current settings intensity."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        trigger = getattr(window, "trigger_screen_shake", None)
        if not callable(trigger):
            return
        settings = getattr(window, "runtime_settings", None)
        if settings is None and hasattr(window, "persistence"):
            load_settings = getattr(window.persistence, "load_settings", None)
            if callable(load_settings):
                settings = load_settings()
        intensity = (
            str(getattr(settings, "screen_shake", "medium"))
            if settings is not None
            else "medium"
        )
        trigger(intensity)

    def _resolve_difficulty_preset(self) -> DifficultyPreset:
        """Load the active difficulty preset from persisted settings."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return DifficultyPreset.CLASSIC
        persistence = getattr(window, "persistence", None)
        if persistence is None or not hasattr(persistence, "load_settings"):
            return DifficultyPreset.CLASSIC
        settings = persistence.load_settings()
        difficulty_value = getattr(settings, "difficulty", DifficultyPreset.CLASSIC)
        return parse_difficulty_preset(str(difficulty_value))

    def _params_for_level(self, level: int) -> DifficultyParams:
        """Return preset-adjusted difficulty parameters for a level."""
        base = get_difficulty_params(level)
        params = self.difficulty_scaler.apply_preset(base, self._difficulty_preset)
        return self._apply_practice_params(params)

    def _apply_practice_params(self, params: DifficultyParams) -> DifficultyParams:
        """Return difficulty params adjusted for practice-mode toggles."""
        if not self._is_practice:
            return params
        if self._practice_asteroids_only:
            params.enemy_spawn_enabled = False
            params.enemy_count_max = 0
            params.enemy_aggression = 0.0
            params.aggressive_ratio = 0.0
            params.enemy_spawn_interval = 99.0
        if self._practice_reduced_count:
            params.asteroid_count = max(1, int(round(params.asteroid_count * 0.5)))
        return params

    def _respawn_practice_ship(self) -> None:
        """Respawn ship in-place for low-stakes practice sessions."""
        window = arcade.get_window()
        ship = self.player_ship
        ship.shields = ship.max_shields
        ship.center_x = window.width / 2
        ship.center_y = window.height / 2
        ship.velocity_x = 0.0
        ship.velocity_y = 0.0
        self.damage_effects.trigger_invulnerability(ship, 2.0)
        self.particle_system.emit_sparkle(ship.center_x, ship.center_y)
        self._game_over_delay_remaining = 0.0

    def _apply_runtime_difficulty(self, params: DifficultyParams) -> None:
        """Apply level difficulty values to runtime systems."""
        self._current_difficulty_params = params
        preset_multipliers = self._difficulty_scaler_for_current_preset()
        self._damage_received_multiplier = preset_multipliers.damage_received
        self.collision_system.damage_received_multiplier = (
            self._damage_received_multiplier
        )
        self.collision_system.currency_drop_chance_override = (
            params.currency_drop_chance
        )

    def _difficulty_scaler_for_current_preset(self) -> DifficultyMultipliers:
        """Return multiplier object for the currently selected difficulty preset."""
        return DIFFICULTY_PRESET_MULTIPLIERS[self._difficulty_preset]

    def _physics_step_performance(self, dt: float) -> None:
        """Advance stress-scene entities while keeping target counts stable."""
        window = arcade.get_window()
        screen_width = float(window.width)
        screen_height = float(window.height)

        player = self.player_ship
        player.center_x += player.velocity_x * dt
        player.center_y += player.velocity_y * dt
        wrap_entity(player, screen_width, screen_height)

        for asteroid in self.entity_manager.asteroids:
            asteroid.update(dt)
            wrap_entity(asteroid, screen_width, screen_height)

        for enemy in self.entity_manager.enemies:
            enemy.center_x += enemy.velocity_x * dt
            enemy.center_y += enemy.velocity_y * dt
            wrap_entity(enemy, screen_width, screen_height)

        for projectile in self.entity_manager.player_projectiles:
            projectile.center_x += projectile.velocity_x * dt
            projectile.center_y += projectile.velocity_y * dt
            wrap_entity(projectile, screen_width, screen_height)

        for projectile in self.entity_manager.enemy_projectiles:
            projectile.center_x += projectile.velocity_x * dt
            projectile.center_y += projectile.velocity_y * dt
            wrap_entity(projectile, screen_width, screen_height)

        for pickup in self.entity_manager.currency_pickups:
            pickup.center_x += pickup.velocity_x * dt
            pickup.center_y += pickup.velocity_y * dt
            wrap_entity(pickup, screen_width, screen_height)

        self.particle_system.update(dt)
        self._apply_visual_settings()

    def _setup_performance_stress_scene(
        self,
        screen_width: int,
        screen_height: int,
    ) -> None:
        """Populate a deterministic peak-load scene for performance profiling."""
        rng = random.Random(self._perf_seed)
        self.entity_manager.clear_projectiles()
        self.entity_manager.clear_enemies()
        self.entity_manager.asteroids.clear()
        self.entity_manager.currency_pickups.clear()
        self.entity_manager.buff_pickups.clear()
        self.entity_manager.particles.clear()
        self.particle_system = ParticleSystem(
            self.entity_manager.particles,
            rng=random.Random(self._perf_seed + 1),
            max_particles=PERF_TARGET_COUNTS["particles"],
        )

        player = self.player_ship
        player.center_x = screen_width / 2
        player.center_y = screen_height / 2
        player.velocity_x = 35.0
        player.velocity_y = 28.0
        player.angle = 0.0
        player.shields = player.max_shields

        asteroid_sizes = [AsteroidSize.LARGE, AsteroidSize.MEDIUM, AsteroidSize.SMALL]
        for index in range(PERF_TARGET_COUNTS["asteroids"]):
            size = asteroid_sizes[index % len(asteroid_sizes)]
            speed = rng.uniform(70.0, 220.0)
            angle = rng.uniform(0.0, math.tau)
            self.entity_manager.asteroids.append(
                Asteroid(
                    size=size,
                    center_x=rng.uniform(0.0, float(screen_width)),
                    center_y=rng.uniform(0.0, float(screen_height)),
                    velocity=(math.cos(angle) * speed, math.sin(angle) * speed),
                    rotation_speed=rng.uniform(20.0, 120.0),
                    rng=rng,
                )
            )

        basic_config = get_basic_config()
        aggressive_config = get_aggressive_config()
        for index in range(PERF_TARGET_COUNTS["enemies"]):
            archetype = EnemyKind.BASIC if index % 2 == 0 else EnemyKind.AGGRESSIVE
            config = basic_config if archetype is EnemyKind.BASIC else aggressive_config
            enemy = EnemyShip(
                archetype=archetype,
                config=config,
                center_x=rng.uniform(0.0, float(screen_width)),
                center_y=rng.uniform(0.0, float(screen_height)),
                rng=rng,
            )
            theta = rng.uniform(0.0, math.tau)
            enemy.velocity_x = math.cos(theta) * config.speed
            enemy.velocity_y = math.sin(theta) * config.speed
            self.entity_manager.enemies.append(enemy)

        for _ in range(PERF_TARGET_COUNTS["player_projectiles"]):
            speed = rng.uniform(600.0, 900.0)
            projectile = Projectile(
                center_x=rng.uniform(0.0, float(screen_width)),
                center_y=rng.uniform(0.0, float(screen_height)),
                angle=rng.uniform(0.0, 360.0),
                speed=speed,
                max_range=max(float(screen_width), float(screen_height)) * 2.0,
                damage=1.0,
                owner=ProjectileOwner.PLAYER,
            )
            self.entity_manager.player_projectiles.append(projectile)

        enemy_projectile_texture = arcade.load_texture(
            str(get_asset_path("sprites", "projectile_enemy.png"))
        )
        for _ in range(PERF_TARGET_COUNTS["enemy_projectiles"]):
            speed = rng.uniform(300.0, 550.0)
            projectile = Projectile(
                center_x=rng.uniform(0.0, float(screen_width)),
                center_y=rng.uniform(0.0, float(screen_height)),
                angle=rng.uniform(0.0, 360.0),
                speed=speed,
                max_range=max(float(screen_width), float(screen_height)) * 2.0,
                damage=1.0,
                owner=ProjectileOwner.ENEMY,
            )
            projectile.texture = enemy_projectile_texture
            self.entity_manager.enemy_projectiles.append(projectile)

        for _ in range(PERF_TARGET_COUNTS["pickups"]):
            pickup = CurrencyPickup(
                center_x=rng.uniform(0.0, float(screen_width)),
                center_y=rng.uniform(0.0, float(screen_height)),
                value=10,
                lifetime=60.0 * 60.0,
                rng=rng,
            )
            self.entity_manager.currency_pickups.append(pickup)

        while (
            self.particle_system.active_particle_count < PERF_TARGET_COUNTS["particles"]
        ):
            self.particle_system.emit_purchase_burst(
                rng.uniform(0.0, float(screen_width)),
                rng.uniform(0.0, float(screen_height)),
            )

        self.game_state.current_level = 99
        self.game_state.score = 999_999
        self.game_state.currency = 99_999

    def _finish_performance_run(self) -> None:
        """Persist stress-run metrics and close the window."""
        if self._perf_finished:
            return
        self._perf_finished = True
        fps_samples = [1000.0 / ms for ms in self._perf_frame_times_ms if ms > 0.0]
        frame_times = self._perf_frame_times_ms
        metrics = {
            "mode": "stress",
            "target_counts": PERF_TARGET_COUNTS,
            "duration_seconds": self._perf_elapsed_seconds,
            "wall_clock_seconds": max(
                0.0,
                time.monotonic() - self._perf_started_at_monotonic,
            ),
            "frame_count": len(frame_times),
            "frame_time_ms": {
                "min": min(frame_times) if frame_times else 0.0,
                "max": max(frame_times) if frame_times else 0.0,
                "mean": statistics.fmean(frame_times) if frame_times else 0.0,
                "median": statistics.median(frame_times) if frame_times else 0.0,
                "p95": _percentile(frame_times, 95.0),
                "p99": _percentile(frame_times, 99.0),
            },
            "fps": {
                "min": min(fps_samples) if fps_samples else 0.0,
                "max": max(fps_samples) if fps_samples else 0.0,
                "mean": statistics.fmean(fps_samples) if fps_samples else 0.0,
            },
            "thresholds": {
                "mean_under_16_67_ms": bool(
                    frame_times and statistics.fmean(frame_times) < 16.67
                ),
                "max_under_33_ms": bool(frame_times and max(frame_times) <= 33.0),
            },
        }

        output_path = self._perf_output_path or os.environ.get(
            "VOIDBREAKER_PERF_OUTPUT"
        )
        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
            print(f"PERF_METRICS_PATH={path}")
        print("PERF_METRICS_JSON_START")
        print(json.dumps(metrics))
        print("PERF_METRICS_JSON_END")
        arcade.get_window().close()


def _percentile(values: list[float], percentile: float) -> float:
    """Return percentile value using nearest-rank interpolation."""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    rank = int(round((percentile / 100.0) * (len(sorted_values) - 1)))
    rank = max(0, min(len(sorted_values) - 1, rank))
    return sorted_values[rank]
