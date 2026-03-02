"""Visual transition, screen shake, and colorblind palette utilities."""

from __future__ import annotations

import math
import random

import arcade

FADE_OUT_SECONDS = 0.3
HOLD_SECONDS = 0.8
FADE_IN_SECONDS = 0.3
TOTAL_DURATION_SECONDS = FADE_OUT_SECONDS + HOLD_SECONDS + FADE_IN_SECONDS

SHAKE_DURATIONS: dict[str, float] = {
    "off": 0.0,
    "low": 0.35,
    "medium": 0.45,
}
SHAKE_INTENSITIES: dict[str, float] = {
    "off": 0.0,
    "low": 3.0,
    "medium": 8.0,
}

COLORBLIND_PALETTE: dict[str, tuple[int, int, int]] = {
    "player": (250, 230, 80),
    "asteroid": (200, 200, 200),
    "enemy": (213, 94, 0),
    "player_projectile": (0, 114, 178),
    "enemy_projectile": (204, 121, 167),
    "currency": (230, 159, 0),
    "buff_heal": (80, 200, 255),
    "buff_damage": (160, 90, 210),
    "buff_speed": (0, 158, 115),
    "shop_weapon": (180, 70, 20),
    "shop_defense": (40, 120, 220),
    "shop_mobility": (20, 220, 120),
    "shop_economy": (220, 180, 40),
    "shop_repair": (245, 245, 245),
    "shop_insurance": (120, 40, 160),
}


class TransitionEffect:
    """Manage a fade-out/hold/fade-in level transition overlay."""

    def __init__(self, width: float, height: float) -> None:
        """Initialise transition dimensions and timer state."""
        self._width = width
        self._height = height
        self._elapsed = 0.0
        self._level = 1
        self.is_active = False

    def start_level_transition(self, level: int) -> None:
        """Start a transition sequence for the provided level number."""
        self._level = max(1, int(level))
        self._elapsed = 0.0
        self.is_active = True

    def update(self, dt: float) -> bool:
        """Advance transition timers and return True once complete."""
        if not self.is_active:
            return True
        self._elapsed = min(TOTAL_DURATION_SECONDS, self._elapsed + max(0.0, dt))
        if self._elapsed >= TOTAL_DURATION_SECONDS - 1e-6:
            self.is_active = False
            return True
        return False

    def draw(self) -> None:
        """Render transition overlay and level text according to current phase."""
        if not self.is_active:
            return
        alpha = self._current_alpha()
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            self._width,
            self._height,
            (0, 0, 0, alpha),
        )
        if self._elapsed >= FADE_OUT_SECONDS:
            arcade.draw_text(
                f"Level {self._level}",
                self._width / 2,
                self._height / 2,
                arcade.color.WHITE,
                42,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            )

    def _current_alpha(self) -> int:
        if self._elapsed < FADE_OUT_SECONDS:
            progress = self._elapsed / FADE_OUT_SECONDS
            return int(255.0 * progress)
        if self._elapsed < FADE_OUT_SECONDS + HOLD_SECONDS:
            return 255
        fade_in_elapsed = self._elapsed - (FADE_OUT_SECONDS + HOLD_SECONDS)
        progress = fade_in_elapsed / FADE_IN_SECONDS
        return int(255.0 * max(0.0, 1.0 - progress))


class ScreenShake:
    """Track time-decayed shake offsets for impact feedback."""

    def __init__(self, rng: random.Random | None = None) -> None:
        """Set initial screen-shake state."""
        self._rng = rng if rng is not None else random.Random()
        self._max_intensity = 0.0
        self._remaining = 0.0
        self._duration = 0.0
        self._offset = (0.0, 0.0)

    def trigger(self, intensity: str) -> None:
        """Reset shake to preset intensity without accumulation."""
        key = intensity.lower().strip()
        target = SHAKE_INTENSITIES.get(key, 0.0)
        duration = SHAKE_DURATIONS.get(key, 0.0)
        self._max_intensity = target
        self._remaining = duration
        self._duration = duration
        if target <= 0.0 or duration <= 0.0:
            self._offset = (0.0, 0.0)

    def update(self, dt: float) -> None:
        """Advance shake decay and refresh the active random offset."""
        if self._remaining <= 0.0 or self._max_intensity <= 0.0:
            self._offset = (0.0, 0.0)
            self._remaining = 0.0
            return

        self._remaining = max(0.0, self._remaining - max(0.0, dt))
        if self._duration <= 0.0:
            scale = 0.0
        else:
            decay = self._remaining / self._duration
            scale = decay * decay
        current_intensity = self._max_intensity * scale
        self._offset = (
            self._rng.uniform(-current_intensity, current_intensity),
            self._rng.uniform(-current_intensity, current_intensity),
        )

    def get_offset(self) -> tuple[float, float]:
        """Return current X/Y shake offset in pixels."""
        return self._offset


def apply_colorblind_palette(
    sprites: arcade.SpriteList[arcade.Sprite],
    enabled: bool,
    *,
    default_color: tuple[int, int, int],
    colorblind_color: tuple[int, int, int],
) -> None:
    """Apply default or colorblind tint to all sprites in a sprite list."""
    target = colorblind_color if enabled else default_color
    for sprite in sprites:
        sprite.color = target


def apply_colorblind_palette_to_combat(entity_manager: object, enabled: bool) -> None:
    """Apply colorblind-safe combat palette to active combat entities."""
    player = getattr(entity_manager, "player_ship", None)
    if player is not None:
        player.color = COLORBLIND_PALETTE["player"] if enabled else arcade.color.WHITE

    apply_colorblind_palette(
        getattr(entity_manager, "asteroids"),
        enabled,
        default_color=arcade.color.WHITE,
        colorblind_color=COLORBLIND_PALETTE["asteroid"],
    )
    apply_colorblind_palette(
        getattr(entity_manager, "enemies"),
        enabled,
        default_color=arcade.color.WHITE,
        colorblind_color=COLORBLIND_PALETTE["enemy"],
    )
    apply_colorblind_palette(
        getattr(entity_manager, "player_projectiles"),
        enabled,
        default_color=arcade.color.WHITE,
        colorblind_color=COLORBLIND_PALETTE["player_projectile"],
    )
    apply_colorblind_palette(
        getattr(entity_manager, "enemy_projectiles"),
        enabled,
        default_color=arcade.color.WHITE,
        colorblind_color=COLORBLIND_PALETTE["enemy_projectile"],
    )
    apply_colorblind_palette(
        getattr(entity_manager, "currency_pickups"),
        enabled,
        default_color=arcade.color.WHITE,
        colorblind_color=COLORBLIND_PALETTE["currency"],
    )

    for buff_pickup in getattr(entity_manager, "buff_pickups"):
        if not enabled:
            buff_pickup.color = arcade.color.WHITE
            continue
        key = f"buff_{buff_pickup.buff_type.value.split('_')[0]}"
        buff_pickup.color = COLORBLIND_PALETTE.get(key, arcade.color.WHITE)


def apply_colorblind_palette_to_shop_nodes(
    shop_nodes: arcade.SpriteList[arcade.Sprite], enabled: bool
) -> None:
    """Apply colorblind-safe tints to shop node sprites."""
    for node in shop_nodes:
        if not enabled:
            node.color = arcade.color.WHITE
            continue

        if getattr(node, "is_insurance_node", False):
            node.color = COLORBLIND_PALETTE["shop_insurance"]
            continue

        upgrade_definition = getattr(node, "upgrade_definition", None)
        if upgrade_definition is None:
            node.color = arcade.color.WHITE
            continue
        category_value = str(getattr(upgrade_definition.category, "value", ""))
        key = f"shop_{category_value}"
        node.color = COLORBLIND_PALETTE.get(key, arcade.color.WHITE)


def palette_is_distinguishable() -> bool:
    """Return True when palette colors are sufficiently distinct from each other."""
    values = list(COLORBLIND_PALETTE.values())
    minimum_distance = min(
        _distance(values[i], values[j])
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return minimum_distance >= 25.0


def _distance(
    lhs: tuple[int, int, int],
    rhs: tuple[int, int, int],
) -> float:
    return math.sqrt(
        float((lhs[0] - rhs[0]) ** 2 + (lhs[1] - rhs[1]) ** 2 + (lhs[2] - rhs[2]) ** 2)
    )
