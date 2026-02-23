"""Manager for applying, tracking, and expiring active player buffs."""

from __future__ import annotations

from asterax.app.src.entities.buff_pickup import BuffType
from asterax.app.src.entities.player_ship import PlayerShip


class BuffManager:
    """Track active temporary buffs and keep player stats in sync."""

    def __init__(self) -> None:
        """Initialise with no active temporary buffs."""
        self._active_buffs: dict[BuffType, tuple[float, float]] = {}

    def apply_buff(
        self, buff_type: BuffType, magnitude: float, duration: float, ship: PlayerShip
    ) -> None:
        """Apply a buff effect to the player ship, refreshing same-type durations."""
        if buff_type is BuffType.HEAL:
            heal_amount = max(0.0, magnitude) * ship.max_shields
            ship.shields = min(ship.max_shields, ship.shields + heal_amount)
            return

        clamped_duration = max(0.0, duration)
        if buff_type is BuffType.DAMAGE_BOOST:
            ship.apply_damage_boost(magnitude)
            self._active_buffs[buff_type] = (clamped_duration, magnitude)
            return

        if buff_type is BuffType.SPEED_BOOST:
            ship.apply_speed_boost(magnitude)
            self._active_buffs[buff_type] = (clamped_duration, magnitude)

    def update(self, dt: float, ship: PlayerShip) -> None:
        """Advance active buff timers and remove expired effects from the ship."""
        expired: list[BuffType] = []
        for buff_type, (remaining, magnitude) in self._active_buffs.items():
            next_remaining = remaining - dt
            if next_remaining <= 0.0:
                expired.append(buff_type)
                continue
            self._active_buffs[buff_type] = (next_remaining, magnitude)

        for buff_type in expired:
            if buff_type is BuffType.DAMAGE_BOOST:
                ship.remove_damage_boost()
            elif buff_type is BuffType.SPEED_BOOST:
                ship.remove_speed_boost()
            self._active_buffs.pop(buff_type, None)

    def get_active_buffs(self) -> list[tuple[BuffType, float]]:
        """Return active timed buffs and their remaining durations."""
        return [
            (buff_type, remaining)
            for buff_type, (remaining, _) in self._active_buffs.items()
        ]

    def clear_all(self, ship: PlayerShip) -> None:
        """Remove all active buffs and restore modified ship stats."""
        if BuffType.DAMAGE_BOOST in self._active_buffs:
            ship.remove_damage_boost()
        if BuffType.SPEED_BOOST in self._active_buffs:
            ship.remove_speed_boost()
        self._active_buffs.clear()
