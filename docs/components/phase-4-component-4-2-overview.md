# Phase 4 Component 4.2 Overview — Shop Phase State & Layout

## Scope Delivered
- Implemented `ShopPhaseState` as a real between-level state (replacing the Phase 1 stub).
- Added circular shop-node layout generation around playfield center.
- Enabled ship piloting in shop via existing thrust/rotation/brake input mapping.
- Disabled wrap-around during shop by clamping the ship to window bounds.
- Added bidirectional phase flow:
  - Combat level clear -> Shop
  - Shop continue collision or Enter key -> next-level Combat

## Implementation Summary
- `app/src/states/shop.py`
  - Added full lifecycle methods: `on_enter`, `on_exit`, `on_update`, `on_draw`, `on_key_press`.
  - Added `_generate_node_layout()` using configurable radius (`SHOP_LAYOUT_CONFIG`).
  - Added `_clamp_ship_to_bounds()` to replace wrap logic.
  - Added continue-node detection and `_transition_to_combat()` handoff.
  - Draws node labels and current currency HUD text.
- `app/src/states/combat.py`
  - Updated level-clear path to transition to `ShopPhaseState` instead of immediate next-wave spawn.
  - Added state handoff data for shop/combat continuity (level, score, currency, run stats, ship angle/velocity snapshot).
  - Added optional constructor inputs for initializing post-shop combat state.
- `app/src/config/game_config.py`
  - Added `ShopLayoutConfig` and singleton `SHOP_LAYOUT_CONFIG` for radius/continue-node offset tuning.

## Verification
- Added `tests/test_shop_phase_state.py` covering:
  - entry-centre spawn and phase assignment
  - circular node geometry
  - bounds clamping
  - Enter-key transition to next combat level
- Updated combat level-clear unit test to validate shop transition pathway.

## Notes
- Node affordability indicators and purchase logic remain intentionally scoped to Component 4.3+.
- Layout tuning is now data-driven through config constants without changing state logic.
