# Phase 4 Implementation Context

## Component Status Summary
- 4.1 Human Setup & Shop Assets — Completed
- 4.2 Shop Phase State & Layout — Completed
- 4.3 Shop Node Entities & Interaction — Completed
- 4.4 Upgrade Manager & Stat Application — Completed
- 4.5 Insurance Manager & Death Retention — Completed
- 4.6 Currency Manager & Economy Flow — Completed
- 4.7 Ship Re-Centring & Purchase Flow Polish — Not Started
- 4.8 E2E Testing & Documentation — Not Started

## Component 4.1 — Human Setup & Shop Assets
- **Status**: Completed
- **What was built**: All placeholder visual assets required for the Phase 4 shop phase. Seven PNG sprite files were generated via Pillow by extending the existing `scripts/generate_placeholder_sprites.py` script. Two `.wav` sound files were provided by the developer prior to this component.
- **Key files created**:
  - `assets/sprites/shop/orb_weapon.png` — 64×64 red (#E74C3C) orb with glow (RGBA)
  - `assets/sprites/shop/orb_defense.png` — 64×64 blue (#3498DB) orb with glow (RGBA)
  - `assets/sprites/shop/orb_mobility.png` — 64×64 green (#2ECC71) orb with glow (RGBA)
  - `assets/sprites/shop/orb_economy.png` — 64×64 gold (#F1C40F) orb with glow (RGBA)
  - `assets/sprites/shop/orb_repair.png` — 64×64 white (#ECF0F1) orb with glow (RGBA)
  - `assets/sprites/shop/orb_insurance.png` — 64×64 purple (#9B59B6) orb with glow (RGBA)
  - `assets/sprites/shop/node_continue.png` — 64×64 green right-pointing arrow (RGBA)
- **Key files modified**:
  - `scripts/generate_placeholder_sprites.py` — added `generate_shop_orb()` and `generate_shop_continue()` functions, `SHOP_DIR` constant, and shop generation calls in `main()`
  - `scripts/verify_assets.py` — added `SHOP_SPRITES_DIR`, shop sprite verification section, and `shop_purchase.wav`/`shop_denied.wav` to sound checks
- **Sound files present** (provided by developer):
  - `assets/sounds/shop_purchase.wav`, `assets/sounds/shop_denied.wav`
- **Design decisions**: Extended existing Pillow sprite generation script rather than creating a separate Phase 4 script, consistent with the Phase 3 approach. Orb sprites use a three-layer design (outer glow ring, main fill circle, inner highlight) for visual depth while remaining placeholder-appropriate. Continue node uses a chevron/arrow shape in green to be visually distinct from the coloured orbs.
- **Deviations**: None from component requirements. All acceptance criteria met.

## Component 4.2 — Shop Phase State & Layout
- **Status**: Completed
- **What was built**: Replaced the Phase 1 shop stub with a functional `ShopPhaseState` that centres the ship on entry, preserves thrust/rotation movement, disables wrap by clamping to screen bounds, and generates a circular shop-node layout with a dedicated continue node at the bottom. Added transition wiring so cleared combat waves now route to shop, and shop transitions back to combat with incremented level/difficulty context.
- **Key files created**:
  - `tests/test_shop_phase_state.py` — targeted shop-phase tests for entry setup, circular layout geometry, clamp behaviour, and enter-to-combat transition.
  - `docs/components/phase-4-component-4-2-overview.md` — component summary for future implementation context.
- **Key files modified**:
  - `app/src/states/shop.py` — full implementation of shop state lifecycle, node layout, shop movement, continue collision/key transition, and HUD labels.
  - `app/src/states/combat.py` — changed level-clear behaviour to transition into shop; added state handoff payload (level, score, currency, run stats, ship snapshot) for shop/combat round-trip.
  - `app/src/config/game_config.py` — added `ShopLayoutConfig` and `SHOP_LAYOUT_CONFIG` constant for configurable layout radius/continue offset.
  - `tests/test_combat_phase_state.py` — adjusted level-clear assertion to validate shop transition path.
- **Design decisions**: Kept shop layout values centralized in config (radius fraction + continue offset) for later Phase 5 tuning. Used lightweight shop-node view models in `shop.py` to avoid blocking on Component 4.3 entity work while still enabling layout, rendering, and collision checks in 4.2.
- **Deviations**: Deferred node affordability/max-state logic to Component 4.3 as planned; 4.2 currently provides static node labels/cost text to satisfy layout/state requirements without overlapping upcoming entity responsibilities.

## Component 4.3 — Shop Node Entities & Interaction
- **Status**: Completed
- **What was built**: Added reusable `ShopNode` and `ContinueNode` entity classes with geometric cost scaling, purchasability checks, and frame-updated affordability/max-state visual alpha logic. Integrated the shop phase to instantiate real node entities (including upgrade-backed nodes plus insurance placeholder and continue node), render node-owned labels, evaluate node collisions each frame, process purchases (currency deduction + stat level increment + effective-stat recalculation), and apply denied feedback (sound + bounce).
- **Key files created**:
  - `app/src/entities/shop_node.py` — `ShopNode` and `ContinueNode` implementations with label and visual-state methods
  - `tests/test_shop_node.py` — targeted tests for cost scaling, purchase gating, visual-state alpha behavior, and shop-phase purchase collision flow
  - `docs/components/phase-4-component-4-3-overview.md` — component summary for future contributors
- **Key files modified**:
  - `app/src/states/shop.py` — replaced static sprite metadata with entity-backed nodes and added purchase/denied interaction handling
  - `app/src/entities/__init__.py` — exported `ShopNode` and `ContinueNode`
- **Design decisions**: Kept insurance as a non-purchasable placeholder node in 4.3 so visuals/interactions are complete now without pre-empting Phase 4.5 insurance-tier business rules. Reused `ShipState.recalculate_effective_stats()` for immediate stat propagation after purchases to avoid introducing an interim manager abstraction before 4.4.
- **Deviations**: The denied visual feedback uses dimming + bounce + denied sound and reserves explicit crossed-out icon rendering for a later polish pass to keep this component minimal and localized.

## Component 4.4 — Upgrade Manager & Stat Application
- **Status**: Completed
- **What was built**: Implemented `UpgradeManager` as the central authority for upgrade levels, cost scaling, one-shot repairs, score multiplier tracking, and recalculation of effective ship stats plus game-state shields/max shields. Shop purchases now route through the manager instead of mutating ship stats directly.
- **Key files created**:
  - `app/src/managers/upgrade_manager.py` — upgrade level tracking, stat application, repairs, score multiplier, bulk set/get APIs
  - `tests/test_upgrade_manager.py` — focused unit tests for apply/cost/cap/repair/set-level/score-multiplier/definition coverage behavior
  - `docs/components/phase-4-component-4-4-overview.md` — technical component summary for future contributors
- **Key files modified**:
  - `app/src/config/upgrade_definitions.py` — populated full 11-upgrade catalog and added `score_bonus`
  - `app/src/states/shop.py` — integrated `UpgradeManager` into purchase flow and node-level lookups
  - `app/src/managers/__init__.py` — exported `UpgradeManager`
  - `app/src/config/game_config.py` — added `score_bonus_level` and aligned `ShipState.recalculate_effective_stats()` with new stat keys
  - `tests/test_shop_node.py`, `tests/test_config.py` — updated expectations to match revised upgrade balance values
- **Design decisions**: Kept `UPGRADE_DEFINITIONS` as a compatibility alias to `ALL_UPGRADES` so existing imports remain stable while enabling explicit “full catalog” naming for Phase 4.4. Repairs remain non-persistent (`repairs` ID) and are excluded from level retention workflows by manager behavior.
- **Deviations**: None from the 4.4 component requirements; all items are AI-owned and fully implemented in this pass.

## Component 4.5 — Insurance Manager & Death Retention
- **Status**: Completed
- **What was built**: Added a dedicated `InsuranceManager` that owns insurance tier state synchronization, per-level insurance cost scaling, recurring deduction behavior with automatic lapse-to-OFF when unaffordable, and upgrade retention calculations/application for death flow handoff.
- **Key files created**:
  - `app/src/managers/insurance_manager.py` — `InsuranceManager` implementation with tier configs (OFF/BASIC/PREMIUM), `get_tier_cost()`, `deduct_level_cost()`, `calculate_retained_upgrades()`, and `apply_retention()`
  - `tests/test_insurance_manager.py` — focused unit tests for tier updates, cost scaling, deduction success/failure, retention fractions by tier, repairs exclusion, and retention application forwarding
  - `docs/components/phase-4-component-4-5-overview.md` — technical overview for future contributors
- **Key files modified**:
  - `app/src/managers/__init__.py` — exported `InsuranceManager`
- **Design decisions**: Implemented small compatibility helpers inside `InsuranceManager` so it can work with both the current `CurrencyManager` API (`spend`/`get_balance`) and the planned Phase 4.6 API (`can_spend`/`deduct`) without introducing broad refactors.
- **Deviations**: Shop-node tier-cycling UI integration is intentionally deferred to the shop-flow components (`4.7`/`4.8`) while 4.5 delivers the full insurance business logic and test coverage required by this component.

## Component 4.6 — Currency Manager & Economy Flow
- **Status**: Completed
- **What was built**: Rewrote `CurrencyManager` as the single authority for all currency transactions. Added `CurrencyRunStats` dataclass, optional `GameState` backing store, `can_spend()`, `deduct()` (insurance semantic alias for `spend()`), `get_run_stats()`, and strict positive-integer validation (`ValueError` for `amount <= 0`). Wired `CombatPhaseState` to pass its `game_state` to the manager at construction and removed the manual `game_state.currency =` sync. Refactored `CollisionSystem._check_ship_vs_pickups` to write currency exclusively through the manager with a no-manager fallback.
- **Key files created/modified**:
  - `app/src/managers/currency_manager.py` — full rewrite with `CurrencyRunStats` and full API
  - `app/src/managers/__init__.py` — added `CurrencyRunStats` export
  - `app/src/states/combat.py` — `game_state` created before `currency_manager`; manager receives `game_state`; manual sync removed
  - `app/src/physics/collisions.py` — `_check_ship_vs_pickups` now routes through manager exclusively
  - `tests/test_currency.py` — rewritten with updated pickup test + 15 Phase 4.6 unit tests
  - `tests/test_currency_pickups.py` — `test_ship_collects_pickups_and_earns_currency` updated to pass `game_state` to manager
  - `docs/components/phase-4-component-4-6-overview.md` — created
- **Design decisions**: Made `game_state` optional (not required) so existing tests and standalone usages continue without modification. `deduct()` delegates to `spend()` — single deduction path avoids divergence. `CurrencyRunStats` is a dataclass rather than a plain tuple for clarity at the game-over summary call site.
- **Deviations**: None from component requirements. All 177 tests pass; evals pass.
