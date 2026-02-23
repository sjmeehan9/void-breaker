"""Shop phase state with circular layout, ship movement, and continue transition."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import arcade
from asterax.app.src.config.game_config import (
    PHYSICS_CONFIG,
    SHOP_LAYOUT_CONFIG,
    GamePhase,
)
from asterax.app.src.config.game_config import GameState as RunGameState
from asterax.app.src.config.game_config import (
    ShipState,
)
from asterax.app.src.entities.player_ship import PlayerShip
from asterax.app.src.states.base_state import BaseState

if TYPE_CHECKING:
    from asterax.app.src.states.state_machine import StateMachine


@dataclass(slots=True)
class _ShopNodeView:
    """View model for rendering and interaction metadata for a shop node."""

    sprite: arcade.Sprite
    label: str
    level_text: str
    cost_text: str
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
        self.shop_nodes = arcade.SpriteList(use_spatial_hash=True)
        self._node_views: list[_ShopNodeView] = []
        self._continue_node: arcade.Sprite | None = None
        self._transitioning_out = False

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
        self._generate_node_layout(window.width, window.height)

    def on_exit(self) -> None:
        """Clear node data prior to transitioning back to combat."""
        self.shop_nodes.clear()
        self._node_views.clear()
        self._continue_node = None

    def on_update(self, delta_time: float) -> None:
        """Apply shop movement controls and check continue-node transition."""
        if self.player_ship is None:
            return
        window = arcade.get_window()
        input_manager = window.input_manager
        if input_manager.is_action_held(
            "rotate_left"
        ) and not input_manager.is_action_held("rotate_right"):
            self.player_ship.apply_rotation(delta_time, direction=1)
        elif input_manager.is_action_held(
            "rotate_right"
        ) and not input_manager.is_action_held("rotate_left"):
            self.player_ship.apply_rotation(delta_time, direction=-1)
        if input_manager.is_action_held("thrust"):
            self.player_ship.apply_thrust(delta_time)
        if input_manager.is_action_held("brake"):
            self.player_ship.apply_brake(delta_time)
        self.player_ship.apply_drag(delta_time)
        self.player_ship.cap_speed()
        self.player_ship.update_position(delta_time)
        self.player_ship.update_cooldown(delta_time)
        self._clamp_ship_to_bounds(window.width, window.height)
        self._check_continue_transition()

    def on_draw(self) -> None:
        """Draw shop nodes, player ship, and lightweight node/currency labels."""
        self.shop_nodes.draw()
        if self.player_ship is not None:
            self.player_ship.draw()
        for node_view in self._node_views:
            y_offset = 54 if node_view.is_continue else -54
            arcade.draw_text(
                f"{node_view.label}\n{node_view.level_text}   {node_view.cost_text}",
                node_view.sprite.center_x,
                node_view.sprite.center_y + y_offset,
                arcade.color.WHITE,
                12,
                anchor_x="center",
                multiline=True,
                align="center",
                width=200,
            )
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

        if key == arcade.key.ESCAPE:
            self.state_machine.push_state(PauseState(self.state_machine))
        elif key == arcade.key.ENTER:
            self._transition_to_combat()

    def _generate_node_layout(self, width: float, height: float) -> None:
        """Generate a circular node arrangement with continue at the bottom."""
        center_x = width / 2
        center_y = height / 2
        radius = (
            min(width, height) * SHOP_LAYOUT_CONFIG.radius_fraction_of_min_dimension
        )
        shop_dir = Path(__file__).resolve().parents[3] / "assets/sprites/shop"
        node_definitions = [
            ("Weapons", "Lv 0/5", "20c", shop_dir / "orb_weapon.png"),
            ("Defense", "Lv 0/5", "25c", shop_dir / "orb_defense.png"),
            ("Mobility", "Lv 0/5", "20c", shop_dir / "orb_mobility.png"),
            ("Economy", "Lv 0/5", "15c", shop_dir / "orb_economy.png"),
            ("Repairs", "Lv 0/5", "30c", shop_dir / "orb_repair.png"),
            ("Insurance", "Lv 0/3", "35c", shop_dir / "orb_insurance.png"),
        ]
        angle_step = 360.0 / len(node_definitions)
        self.shop_nodes.clear()
        self._node_views.clear()
        for index, (label, level_text, cost_text, texture_path) in enumerate(
            node_definitions
        ):
            angle_radians = math.radians(90.0 - (index * angle_step))
            sprite = arcade.Sprite(
                str(texture_path),
                center_x=center_x + math.cos(angle_radians) * radius,
                center_y=center_y + math.sin(angle_radians) * radius,
            )
            self.shop_nodes.append(sprite)
            self._node_views.append(
                _ShopNodeView(
                    sprite=sprite,
                    label=label,
                    level_text=level_text,
                    cost_text=cost_text,
                )
            )

        continue_sprite = arcade.Sprite(
            str(shop_dir / "node_continue.png"),
            center_x=center_x,
            center_y=center_y - radius - SHOP_LAYOUT_CONFIG.continue_node_extra_offset,
        )
        self.shop_nodes.append(continue_sprite)
        self._continue_node = continue_sprite
        self._node_views.append(
            _ShopNodeView(
                sprite=continue_sprite,
                label="Continue",
                level_text="",
                cost_text="[Enter]",
                is_continue=True,
            )
        )

    def _clamp_ship_to_bounds(self, width: float, height: float) -> None:
        """Clamp ship position to screen bounds (shop disables wrap-around)."""
        if self.player_ship is None:
            return
        self.player_ship.center_x = max(0.0, min(width, self.player_ship.center_x))
        self.player_ship.center_y = max(0.0, min(height, self.player_ship.center_y))

    def _check_continue_transition(self) -> None:
        """Transition back to combat when colliding with the continue node."""
        if (
            self.player_ship is None
            or self._continue_node is None
            or not arcade.check_for_collision(self.player_ship, self._continue_node)
        ):
            return
        self._transition_to_combat()

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
