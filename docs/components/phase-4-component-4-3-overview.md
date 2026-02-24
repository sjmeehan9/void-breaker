# Phase 4 Component 4.3 Overview — Shop Node Entities & Interaction

## Scope Delivered
- Implemented reusable shop node entities:
  - `ShopNode` for upgrade purchases
  - `ContinueNode` for free shop exit action
- Added node-level behavior for:
  - cost calculation (`base_cost * cost_scaling^level`)
  - purchasability checks (affordability + max-level)
  - visual affordability states (pulse, dim, maxed alpha)
  - node-owned label rendering (name, level/MAX, cost)
- Wired shop-phase collision interaction:
  - affordable collision -> deduct currency, apply upgrade, purchase sound
  - denied/maxed collision -> denied sound + slight ship bounce
  - continue collision -> transition back to combat

## Files Changed
- `app/src/entities/shop_node.py` (new)
- `app/src/entities/__init__.py`
- `app/src/states/shop.py`
- `tests/test_shop_node.py` (new)

## Implementation Notes
- `ShopPhaseState` now builds real entity-backed nodes instead of static sprite metadata.
- Upgrade purchases update `ShipState` level fields directly and call `recalculate_effective_stats(...)` for immediate gameplay effect.
- `repair` is handled as an immediate shield restore purchase action.
- Insurance node is represented visually in this component as a non-purchasable placeholder and is intentionally deferred to Phase 4.5 rules.

## Verification
- Added focused tests validating:
  - geometric cost scaling
  - affordability and max-level gating
  - visual alpha transitions for node states
  - end-to-end shop collision purchase behavior in `ShopPhaseState`
