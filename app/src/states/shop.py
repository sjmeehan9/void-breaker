"""Shop phase state with circular layout, ship movement, and continue transition."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import arcade
from asterax.app.src.config.game_config import (
    GAME_CONFIG,
    PHYSICS_CONFIG,
    SHOP_LAYOUT_CONFIG,
    GamePhase,
)
from asterax.app.src.config.game_config import GameState as RunGameState
from asterax.app.src.config.game_config import (
    InsuranceTier,
    ShipState,
)
from asterax.app.src.config.upgrade_definitions import (
    get_upgrade_by_id,
)
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.entities.shop_node import ContinueNode, ShopNode
from asterax.app.src.managers.currency_manager import CurrencyManager
from asterax.app.src.managers.insurance_manager import InsuranceManager
from asterax.app.src.managers.upgrade_manager import UpgradeManager
from asterax.app.src.rendering.particle_system import ParticleSystem
from asterax.app.src.rendering.transitions import apply_colorblind_palette_to_shop_nodes
from asterax.app.src.states.base_state import BaseState

if TYPE_CHECKING:
    from asterax.app.src.states.state_machine import StateMachine


@dataclass(slots=True)
class _ShopNodeView:
    """View model for rendering and interaction metadata for a shop node."""

    sprite: ShopNode
    label: str
    is_continue: bool = False


class ShopPhaseState(BaseState):
    """Between-level shop phase with fly-through node layout and continue flow."""

    def __init__(
        self,
        state_machine: StateMachine,
        game_state: RunGameState | None = None,
        ship_state: ShipState | None = None,
    ) -> None:
        """Initialize a shop phase with optional inherited run and ship state."""
        super().__init__(state_machine)
        self.game_state = game_state or RunGameState()
        self.ship_state = ship_state or ShipState()
        self.player_ship: PlayerShip | None = None
        self.upgrade_manager = UpgradeManager(self.ship_state, self.game_state)
        self.currency_manager = CurrencyManager(self.game_state)
        self.insurance_manager = InsuranceManager(
            self.game_state.insurance,
            self.currency_manager,
            self.upgrade_manager,
        )
        self.shop_nodes = arcade.SpriteList(use_spatial_hash=True)
        self._node_views: list[_ShopNodeView] = []
        self._continue_node: ContinueNode | None = None
        self._interaction_cooldown_seconds = 0.0
        self._transitioning_out = False
        self._recentre_active = False
        self._recentre_elapsed = 0.0
        self._recentre_duration = GAME_CONFIG.shop_recentre_duration
        self._recentre_start_x = 0.0
        self._recentre_start_y = 0.0
        self.particle_system = ParticleSystem()

    def on_enter(self) -> None:
        """Initialize shop ship placement and generate circular node layout."""
        window = arcade.get_window()
        ship_sprite_path = (
            Path(__file__).resolve().parents[3] / "assets/sprites/ship.png"
        )
        self.player_ship = PlayerShip(
            sprite_path=ship_sprite_path,
            center_x=window.width / 2,
            center_y=window.height / 2,
            physics_config=PHYSICS_CONFIG,
        )
        self.player_ship.velocity_x = 0.0
        self.player_ship.velocity_y = 0.0
        self.player_ship.angle = self.ship_state.angle
        self.game_state.phase = GamePhase.SHOP
        self._recentre_active = False
        self._recentre_elapsed = 0.0
        self._generate_node_layout(window.width, window.height)
        self._apply_visual_settings()

    def on_exit(self) -> None:
        """Clear node data prior to transitioning back to combat."""
        self.shop_nodes.clear()
        self._node_views.clear()
        self._continue_node = None
        self._interaction_cooldown_seconds = 0.0
        self._recentre_active = False
        self._recentre_elapsed = 0.0

    def on_update(self, delta_time: float) -> None:
        """Apply shop movement controls and check continue-node transition."""
        if self.player_ship is None:
            return
        self._interaction_cooldown_seconds = max(
            0.0, self._interaction_cooldown_seconds - max(0.0, delta_time)
        )
        window = arcade.get_window()
        if self._is_recentring():
            self._update_recentre(delta_time)
        else:
            input_manager = window.input_manager
            if input_manager.is_action_held(
                "rotate_left"
            ) and not input_manager.is_action_held("rotate_right"):
                self.player_ship.apply_rotation(delta_time, direction=-1)
            elif input_manager.is_action_held(
                "rotate_right"
            ) and not input_manager.is_action_held("rotate_left"):
                self.player_ship.apply_rotation(delta_time, direction=1)
            if input_manager.is_action_held("thrust"):
                self.player_ship.apply_thrust(delta_time)
            if input_manager.is_action_held("brake"):
                self.player_ship.apply_brake(delta_time)
            self.player_ship.apply_drag(delta_time)
            self.player_ship.cap_speed()
            self.player_ship.update_position(delta_time)
            self.player_ship.update_cooldown(delta_time)
            self._clamp_ship_to_bounds(window.width, window.height)
        self._update_node_visual_states(delta_time)
        self._apply_visual_settings()
        self._handle_node_collisions()
        self.particle_system.update(delta_time)

    def on_draw(self) -> None:
        """Draw shop nodes, player ship, and lightweight node/currency labels."""
        self.shop_nodes.draw()
        self.particle_system.draw()
        if self.player_ship is not None:
            arcade.draw_sprite(self.player_ship)
        for node_view in self._node_views:
            node_level = (
                0 if node_view.is_continue else self._get_node_level(node_view.sprite)
            )
            node_view.sprite.draw_label(node_level)
        arcade.draw_text(
            f"Credits: {self.game_state.currency}",
            20,
            arcade.get_window().height - 40,
            arcade.color.WHITE,
            18,
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle pause and continue key shortcuts for the shop phase."""
        del modifiers
        from asterax.app.src.states.pause import PauseState

        if key == self._pause_key():
            self.state_machine.push_state(PauseState(self.state_machine))
        elif key == arcade.key.ENTER:
            self._handle_continue()

    def _pause_key(self) -> int:
        """Return current configured pause key binding.

        Returns:
            Key code for pause action.
        """
        window = arcade.get_window()
        input_manager = getattr(window, "input_manager", None)
        get_binding = getattr(input_manager, "get_binding", None)
        if callable(get_binding):
            return int(get_binding("pause"))
        return arcade.key.ESCAPE

    def _generate_node_layout(self, width: float, height: float) -> None:
        """Generate a circular node arrangement with continue at the bottom."""
        center_x = width / 2
        center_y = height / 2
        radius = (
            min(width, height) * SHOP_LAYOUT_CONFIG.radius_fraction_of_min_dimension
        )
        shop_dir = Path(__file__).resolve().parents[3] / "assets/sprites/shop"
        node_definitions = [
            ("weapon_fire_rate", shop_dir / "orb_weapon.png", None),
            ("defense_shields", shop_dir / "orb_defense.png", None),
            ("mobility_thrust", shop_dir / "orb_mobility.png", None),
            ("economy_magnet", shop_dir / "orb_economy.png", None),
            ("repairs", shop_dir / "orb_repair.png", None),
            (None, shop_dir / "orb_insurance.png", "Insurance"),
        ]
        angle_step = 360.0 / len(node_definitions)
        self.shop_nodes.clear()
        self._node_views.clear()
        for index, (upgrade_id, texture_path, label_override) in enumerate(
            node_definitions
        ):
            angle_radians = math.radians(90.0 - (index * angle_step))
            definition = (
                get_upgrade_by_id(upgrade_id) if isinstance(upgrade_id, str) else None
            )
            sprite = ShopNode(
                texture_path=texture_path,
                center_x=center_x + math.cos(angle_radians) * radius,
                center_y=center_y + math.sin(angle_radians) * radius,
                upgrade_definition=definition,
                label_override=label_override,
                is_insurance_node=upgrade_id is None,
            )
            self.shop_nodes.append(sprite)
            self._node_views.append(
                _ShopNodeView(
                    sprite=sprite,
                    label=sprite.display_name,
                )
            )

        continue_sprite = ContinueNode(
            texture_path=shop_dir / "node_continue.png",
            center_x=center_x,
            center_y=center_y - radius - SHOP_LAYOUT_CONFIG.continue_node_extra_offset,
            upgrade_definition=None,
            label_override="Continue",
        )
        self.shop_nodes.append(continue_sprite)
        self._continue_node = continue_sprite
        self._node_views.append(
            _ShopNodeView(
                sprite=continue_sprite,
                label="Continue",
                is_continue=True,
            )
        )

    def _clamp_ship_to_bounds(self, width: float, height: float) -> None:
        """Clamp ship position to screen bounds (shop disables wrap-around)."""
        if self.player_ship is None:
            return
        self.player_ship.center_x = max(0.0, min(width, self.player_ship.center_x))
        self.player_ship.center_y = max(0.0, min(height, self.player_ship.center_y))

    def _update_node_visual_states(self, delta_time: float) -> None:
        """Refresh affordability visuals for each node each frame."""
        current_currency = self.currency_manager.get_balance()
        for node_view in self._node_views:
            node = node_view.sprite
            if node.is_insurance_node:
                next_tier = self._get_next_insurance_tier()
                insurance_cost = self.insurance_manager.get_tier_cost(
                    next_tier,
                    self.game_state.current_level,
                )
                can_afford = insurance_cost <= 0 or (current_currency >= insurance_cost)
                node.update_visual_state(
                    currency=current_currency,
                    current_level=0,
                    delta_time=delta_time,
                    can_afford_override=can_afford,
                )
                continue
            level = (
                0 if node_view.is_continue else self._get_node_level(node_view.sprite)
            )
            node.update_visual_state(
                currency=current_currency,
                current_level=level,
                delta_time=delta_time,
            )

    def _handle_node_collisions(self) -> None:
        """Handle continue, purchase, and denied collisions."""
        if (
            self.player_ship is None
            or self._interaction_cooldown_seconds > 0.0
            or self._is_recentring()
        ):
            return
        for node_view in self._node_views:
            if not arcade.check_for_collision(self.player_ship, node_view.sprite):
                continue
            self._handle_node_collision(node_view.sprite)
            return

    def _handle_node_collision(self, node: ShopNode) -> None:
        """Route node interactions to continue, insurance, or upgrade purchase."""
        if node.is_continue_node:
            self._handle_continue()
            return
        if node.is_insurance_node:
            self._attempt_insurance_change()
            return
        self._attempt_upgrade_purchase(node)

    def _attempt_upgrade_purchase(self, node: ShopNode) -> None:
        """Attempt an upgrade purchase and apply accepted or denied feedback."""
        current_level = self._get_node_level(node)
        current_currency = self.currency_manager.get_balance()
        if not node.can_purchase(current_currency, current_level):
            self._interaction_cooldown_seconds = 0.2
            self._play_shop_sound("shop_denied")
            self._apply_denied_bounce(node)
            return

        definition = node.upgrade_definition
        if definition is None:
            self._interaction_cooldown_seconds = 0.2
            self._play_shop_sound("shop_denied")
            self._apply_denied_bounce(node)
            return

        cost = self.upgrade_manager.get_cost(definition.id)
        if not self.currency_manager.spend(cost):
            self._interaction_cooldown_seconds = 0.2
            self._play_shop_sound("shop_denied")
            self._apply_denied_bounce(node)
            return

        self.game_state.run_stats.currency_spent += cost
        self.game_state.run_stats.upgrades_purchased += 1

        if not self.upgrade_manager.apply_upgrade(definition.id):
            self.currency_manager.earn(cost)
            self.game_state.run_stats.currency_spent = max(
                0,
                self.game_state.run_stats.currency_spent - cost,
            )
            self._interaction_cooldown_seconds = 0.2
            self._play_shop_sound("shop_denied")
            self._apply_denied_bounce(node)
            return

        self._interaction_cooldown_seconds = 0.2
        self._play_shop_sound("shop_purchase")
        self.particle_system.emit_purchase_burst(
            node.center_x,
            node.center_y,
            color=(140, 255, 200),
        )
        self._start_recentre()

    def _attempt_insurance_change(self) -> None:
        """Cycle to the next insurance tier when the tier-change cost is affordable."""
        next_tier = self._get_next_insurance_tier()
        insurance_cost = self.insurance_manager.get_tier_cost(
            next_tier,
            self.game_state.current_level,
        )
        if insurance_cost > 0 and not self.currency_manager.spend(insurance_cost):
            self._interaction_cooldown_seconds = 0.2
            self._play_shop_sound("shop_denied")
            return

        if insurance_cost > 0:
            self.game_state.run_stats.currency_spent += insurance_cost
        self.insurance_manager.set_tier(next_tier)
        self._interaction_cooldown_seconds = 0.2
        self._play_shop_sound("shop_purchase")
        insurance_node = self._find_insurance_node()
        if insurance_node is not None:
            self.particle_system.emit_purchase_burst(
                insurance_node.center_x,
                insurance_node.center_y,
                color=(186, 128, 255),
            )
        self._start_recentre()

    def _get_node_level(self, node: ShopNode) -> int:
        """Resolve the ship's current level for a node's upgrade."""
        if node.upgrade_definition is None:
            return 0
        return self.upgrade_manager.get_level(node.upgrade_definition.id)

    def _play_shop_sound(self, sound_name: str) -> None:
        """Play a shop sound effect when an audio manager is available."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        if not hasattr(window, "audio_manager"):
            return
        if sound_name == "shop_purchase":
            if hasattr(window.audio_manager, "play_shop_purchase"):
                window.audio_manager.play_shop_purchase()
            else:
                window.audio_manager.play("shop_purchase")
            return
        if sound_name == "shop_denied":
            if hasattr(window.audio_manager, "play_shop_denied"):
                window.audio_manager.play_shop_denied()
            else:
                window.audio_manager.play("shop_denied")
            return
        if sound_name == "level_clear":
            if hasattr(window.audio_manager, "play_level_clear"):
                window.audio_manager.play_level_clear()
            else:
                window.audio_manager.play("level_clear")
            return
        window.audio_manager.play(sound_name)

    def _apply_denied_bounce(self, node: ShopNode) -> None:
        """Apply a slight velocity nudge away from a denied node collision."""
        if self.player_ship is None:
            return
        dx = self.player_ship.center_x - node.center_x
        dy = self.player_ship.center_y - node.center_y
        distance = math.hypot(dx, dy)
        if distance <= 1e-6:
            dx, dy = 0.0, 1.0
            distance = 1.0
        push = 120.0
        self.player_ship.velocity_x = (dx / distance) * push
        self.player_ship.velocity_y = (dy / distance) * push

    def _transition_to_combat(self) -> None:
        """Return to combat on the next level while preserving run totals."""
        if self._transitioning_out:
            return
        self._transitioning_out = True
        self.game_state.current_level += 1
        self.game_state.phase = GamePhase.COMBAT
        from asterax.app.src.states.combat import CombatPhaseState

        self.state_machine.switch_state(
            CombatPhaseState(
                self.state_machine,
                initial_level=self.game_state.current_level,
                initial_score=self.game_state.score,
                initial_currency=self.game_state.currency,
                initial_run_stats=self.game_state.run_stats,
            )
        )

    def _is_recentring(self) -> bool:
        """Return whether the ship is currently interpolating back to center."""
        return self._recentre_active

    def _start_recentre(self) -> None:
        """Start smooth interpolation of the ship back to playfield center."""
        if self.player_ship is None:
            return
        self._recentre_active = True
        self._recentre_elapsed = 0.0
        self._recentre_start_x = self.player_ship.center_x
        self._recentre_start_y = self.player_ship.center_y

    def _update_recentre(self, delta_time: float) -> None:
        """Advance ease-out re-centering interpolation by one frame."""
        if self.player_ship is None:
            return
        duration = max(1e-6, self._recentre_duration)
        self._recentre_elapsed += max(0.0, delta_time)
        progress = min(1.0, self._recentre_elapsed / duration)
        eased_progress = self._ease_out_quadratic(progress)

        window = arcade.get_window()
        target_x = window.width / 2
        target_y = window.height / 2
        self.player_ship.center_x = (
            self._recentre_start_x
            + (target_x - self._recentre_start_x) * eased_progress
        )
        self.player_ship.center_y = (
            self._recentre_start_y
            + (target_y - self._recentre_start_y) * eased_progress
        )
        if progress >= 1.0:
            self._recentre_active = False
            self.player_ship.center_x = target_x
            self.player_ship.center_y = target_y
            self.player_ship.velocity_x = 0.0
            self.player_ship.velocity_y = 0.0

    @staticmethod
    def _ease_out_quadratic(progress: float) -> float:
        """Apply a quadratic ease-out curve to normalized interpolation progress."""
        clamped_progress = max(0.0, min(1.0, progress))
        return 1.0 - ((1.0 - clamped_progress) ** 2)

    def _handle_continue(self) -> None:
        """Apply level-transition side effects then switch back to combat."""
        if self._transitioning_out:
            return
        self._play_shop_sound("level_clear")
        balance_before_deduction = self.currency_manager.get_balance()
        self.insurance_manager.deduct_level_cost(self.game_state.current_level)
        balance_after_deduction = self.currency_manager.get_balance()
        if balance_after_deduction < balance_before_deduction:
            self._play_insurance_deduct_sound()
            self.game_state.run_stats.currency_spent += (
                balance_before_deduction - balance_after_deduction
            )
        self._transition_to_combat()

    def _find_insurance_node(self) -> ShopNode | None:
        """Return insurance node sprite if present in the active layout."""
        for node_view in self._node_views:
            if node_view.sprite.is_insurance_node:
                return node_view.sprite
        return None

    def _play_insurance_deduct_sound(self) -> None:
        """Play insurance deduction sound if an audio manager is available."""
        try:
            window = arcade.get_window()
        except RuntimeError:
            return
        if not hasattr(window, "audio_manager"):
            return
        if hasattr(window.audio_manager, "play_insurance_deduct"):
            window.audio_manager.play_insurance_deduct()
            return
        window.audio_manager.play("insurance_deduct")

    def _get_next_insurance_tier(self) -> InsuranceTier:
        """Return the next tier in OFF -> BASIC -> PREMIUM -> OFF cycle."""
        current_tier = self.insurance_manager.get_tier()
        if current_tier == InsuranceTier.OFF:
            return InsuranceTier.BASIC
        if current_tier == InsuranceTier.BASIC:
            return InsuranceTier.PREMIUM
        return InsuranceTier.OFF

    def _apply_visual_settings(self) -> None:
        """Apply colorblind-safe palette to shop entities when enabled."""
        window = arcade.get_window()
        settings = getattr(window, "runtime_settings", None)
        if settings is None and hasattr(window, "persistence"):
            settings = window.persistence.load_settings()
        colorblind_enabled = bool(
            getattr(settings, "colorblind_mode", False)
            if settings is not None
            else False
        )
        apply_colorblind_palette_to_shop_nodes(self.shop_nodes, colorblind_enabled)
        if self.player_ship is not None:
            self.player_ship.color = (
                (240, 228, 66) if colorblind_enabled else arcade.color.WHITE
            )
