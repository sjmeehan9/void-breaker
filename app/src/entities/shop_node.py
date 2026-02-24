"""Shop node entities for purchasable upgrades and shop navigation."""

from __future__ import annotations

import math
from pathlib import Path

import arcade
from asterax.app.src.config.upgrade_definitions import UpgradeDefinition

_PULSE_MIN_ALPHA = 200
_PULSE_MAX_ALPHA = 255
_UNAFFORDABLE_ALPHA = 100
_MAXED_ALPHA = 150
_PULSE_PERIOD_SECONDS = 1.0


class ShopNode(arcade.Sprite):
    """A purchasable shop upgrade node with affordability-driven visuals."""

    def __init__(
        self,
        *,
        texture_path: Path,
        center_x: float,
        center_y: float,
        upgrade_definition: UpgradeDefinition | None,
        label_override: str | None = None,
    ) -> None:
        """Initialise a shop node sprite with optional upgrade metadata."""
        super().__init__(
            str(texture_path),
            center_x=center_x,
            center_y=center_y,
        )
        self.upgrade_definition = upgrade_definition
        self._label_override = label_override
        self._pulse_time_seconds = 0.0

    @property
    def display_name(self) -> str:
        """Return the display label shown for this node."""
        if self._label_override is not None:
            return self._label_override
        if self.upgrade_definition is None:
            return "Unavailable"
        return self.upgrade_definition.name

    def calculate_cost(self, current_level: int) -> int:
        """Calculate next-level cost from base cost and geometric scaling."""
        if self.upgrade_definition is None:
            return 0
        safe_level = max(0, current_level)
        return int(
            self.upgrade_definition.base_cost
            * (self.upgrade_definition.cost_scaling**safe_level)
        )

    def can_purchase(self, currency: int, current_level: int) -> bool:
        """Return whether this node can currently be purchased."""
        if self.upgrade_definition is None:
            return False
        if current_level >= self.upgrade_definition.max_level:
            return False
        return currency >= self.calculate_cost(current_level)

    def update_visual_state(
        self,
        *,
        currency: int,
        current_level: int,
        delta_time: float,
    ) -> None:
        """Update pulsing/dimmed alpha based on affordability and level cap."""
        if self.upgrade_definition is None:
            self.alpha = _MAXED_ALPHA
            return

        if current_level >= self.upgrade_definition.max_level:
            self.alpha = _MAXED_ALPHA
            return

        if not self.can_purchase(currency, current_level):
            self.alpha = _UNAFFORDABLE_ALPHA
            return

        self._pulse_time_seconds = (
            self._pulse_time_seconds + max(0.0, delta_time)
        ) % _PULSE_PERIOD_SECONDS
        pulse = (math.sin((2.0 * math.pi * self._pulse_time_seconds)) + 1.0) / 2.0
        self.alpha = int(
            _PULSE_MIN_ALPHA + (_PULSE_MAX_ALPHA - _PULSE_MIN_ALPHA) * pulse
        )

    def draw_label(self, current_level: int) -> None:
        """Draw the node label, level text, and cost text under the sprite."""
        if self.upgrade_definition is None:
            level_text = "N/A"
            cost_text = "---"
        elif current_level >= self.upgrade_definition.max_level:
            level_text = "MAX"
            cost_text = "---"
        else:
            level_text = f"Lv {current_level}/{self.upgrade_definition.max_level}"
            cost_text = f"{self.calculate_cost(current_level)}c"

        arcade.draw_text(
            f"{self.display_name}\n{level_text}\n{cost_text}",
            self.center_x,
            self.center_y - 54,
            arcade.color.WHITE,
            12,
            anchor_x="center",
            multiline=True,
            align="center",
            width=220,
        )


class ContinueNode(ShopNode):
    """Shop node variant that exits the shop and starts the next level."""

    def can_purchase(self, currency: int, current_level: int) -> bool:
        """Continue action is always available and has no cost."""
        del currency, current_level
        return True

    def update_visual_state(
        self,
        *,
        currency: int,
        current_level: int,
        delta_time: float,
    ) -> None:
        """Pulse continuously to highlight the continue action."""
        del currency, current_level
        self._pulse_time_seconds = (
            self._pulse_time_seconds + max(0.0, delta_time)
        ) % _PULSE_PERIOD_SECONDS
        pulse = (math.sin((2.0 * math.pi * self._pulse_time_seconds)) + 1.0) / 2.0
        self.alpha = int(
            _PULSE_MIN_ALPHA + (_PULSE_MAX_ALPHA - _PULSE_MIN_ALPHA) * pulse
        )

    def draw_label(self, current_level: int) -> None:
        """Draw only a simple continue label for this node."""
        del current_level
        arcade.draw_text(
            "Continue",
            self.center_x,
            self.center_y + 54,
            arcade.color.WHITE,
            12,
            anchor_x="center",
        )
