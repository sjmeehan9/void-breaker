# Project Brief: Retro Space Shooter (Working Title: "Asterax Tribute")

Version: 1.0
Date: 2026-02-18
Status: Draft — Pending User Approval

---

## Overview

This project is an entirely local, offline arcade space shooter inspired by the classic Mac game Asterax. It faithfully recreates the core gameplay loop — inertial ship handling, asteroid splitting, currency collection, and between-level upgrade purchasing — while using fully original assets and branding. The game targets players who enjoy score-chasing, upgrade-driven runs, and fast "one more run" replayability.

## Problem Statement

Classic Mac shareware arcade shooters like Asterax are no longer readily available on modern platforms. Players who enjoyed the specific combination of Asteroids-style physics, in-run currency economies, and between-level shop mechanics have no faithful modern equivalent. This project fills that gap with a standalone, offline game that captures the original feel while running on current hardware and operating systems.

## Goals & Success Metrics

- **Faithful arcade feel**: Ship handling, collisions, and pacing evoke the original Asterax experience. Measured by playtest feedback confirming the "feel" is right.
- **Complete game loop**: A player can start, play multiple levels, shop for upgrades, die, record a high score, and restart without encountering any blockers. Measured by end-to-end QA pass.
- **Sustained replayability**: Difficulty progression supports at least 30 minutes of skilled play per run. Measured by playtesting difficulty curve.
- **Zero-friction onboarding**: A new player can start playing within seconds of launching the game, with controls discoverable via "How to Play". Measured by first-time user testing.
- **Full offline operation**: The entire experience works with no internet connection, no accounts, and no external dependencies. Verified by disconnected testing.

## Target Users

- **Retro Arcade Enthusiast**: Played classic Mac shareware shooters (Asterax, Maelstrom, Asteroids clones) and wants that experience on a modern machine. Values authentic physics feel and score chasing above all.
- **Casual Arcade Player**: Enjoys pick-up-and-play arcade games with simple controls and escalating challenge. Drawn to the "one more run" loop and upgrade decisions. Does not need deep story or complex systems.
- **Score Chaser**: Motivated by local high score competition (self-improvement or same-household rivalries). Wants clear scoring rules, fair difficulty scaling, and persistent leaderboards.

## Functional Requirements

### Core Gameplay

1. **Ship Controls**: Rotate left/right, thrust/accelerate, fire primary weapon. Optional brake/retro-thrust if consistent with feel. Optional special weapon/ability (purchasable upgrade).
2. **Inertial Physics**: 2D top-down movement with inertia. Responsive, predictable, learnable arcade physics.
3. **Wrap-Around Playfield**: Ship, asteroids, and projectiles wrap edges — exiting one side re-enters from the opposite.
4. **Asteroid System**: Three sizes (large/medium/small). Destroying a larger asteroid splits it into multiple smaller ones. Smallest size is fully destructible.
5. **Enemy Ships**: Appear after early levels and escalate. Minimum two archetypes: basic shooter (slow, simple pattern) and aggressive (faster, higher rate of fire). Optional sniper archetype. Must telegraph attacks and be "fair" — no cheap deaths.
6. **Projectile System**: Primary weapon fires projectiles with maximum range/lifetime. Optional on-screen projectile cap to encourage timing over spam.
7. **Collision & Damage**: Collisions with asteroids or enemy fire cause damage. Clear feedback: flash, sound, optional brief invulnerability window. Shields-only survival model — when shields/hull reach zero, the run ends immediately.
8. **Currency Drops**: Destroyed asteroids have a chance to drop currency pickups. Collected by flying over them. Clear visual identity and collection sound. Optional timeout on uncollected pickups. Optional rule: currency pickups can be destroyed by stray shots (preventable via upgrade).
9. **Additional Pickups** (optional): Rare drops providing temporary buffs — small heal, temporary shield, damage boost, speed boost.

### Shop / Upgrade System (Signature Feature)

10. **Between-Level Shop**: Appears after each combat phase. Player spends currency on upgrades before the next level. Target interaction time: 5-20 seconds.
11. **Asterax-Style Shop Interaction**: Player controls the ship during the shop phase. Items represented as floating nodes/orbs; player flies into a node to purchase. Ship re-centers after purchase. UI clearly shows current currency, item cost, item effect, and current upgrade level.
12. **Upgrade Categories** (minimum):
    - **Weapons**: Fire rate, damage, projectile speed/range, spread/multi-shot (optional).
    - **Defense**: Shields/armor, damage reduction (optional).
    - **Mobility**: Thrust power, turn rate, drift control (optional).
    - **Economy/Utility**: Pickup magnet/attraction radius, "currency can't be destroyed" (optional), increased drop rate (optional, balance carefully).
    - **Repairs**: Restore shields/hull (no free heal between levels).
13. **Score Bonuses** (optional): Purchasable score multipliers that trade survivability for points.
14. **Insurance System**: Buyable insurance plan costing currency each level. Tiers: retain all upgrades (premium), retain a subset (basic), retain nothing (off). Included in v1.0.

### Levels & Progression

15. **Level Structure**: Each level has a combat phase (asteroids + enemies), pickup phase (collect currency under pressure), and transition to shop.
16. **Difficulty Scaling**: Across levels, increase asteroid count, speed, spawn pressure, and enemy frequency/aggression. Early levels teach fundamentals; mid levels force upgrade decisions; late levels are intense but fair. No sudden impossible spikes.
17. **Endless Mode**: The game is primarily endless. A run ends only when shields/hull reach zero.
18. **Ship Classes** (recommended, optional): Nimble (faster turning, lower durability), Tank (slower, higher durability), Balanced (middle ground).

### Scoring & High Scores

19. **Scoring Rules**: Points for destroying asteroids (scaled by size) and enemies. Optional bonuses for fast level clears, no-damage levels, or collecting all currency drops.
20. **Local High Score Table**: Persistent local leaderboard with name/initials, score, level reached, difficulty setting, and date/time. Separate leaderboards per difficulty.

### Game Modes

21. **Classic Endless** (default): Standard rules, endless progression, local high scores.
22. **Practice/Training** (recommended): Low-stakes sandbox for learning. Toggles for asteroids only, no enemies, infinite shields.
23. **Challenge Variants** (optional): "No shop" survival, "double enemies", "low visibility", time attack.

### UI/UX

24. **Main Menu**: New Game, How to Play, Settings, High Scores, Quit.
25. **In-Game HUD**: Shields/hull, current score, current level, currency amount. Optional weapon/upgrade indicators.
26. **Pause System**: Instant freeze. Menu with Resume, Restart Run, Settings, Exit to Menu.
27. **Game Over Screen**: Run summary showing score, level reached, enemies destroyed, currency collected/spent. High score entry prompt if qualified.

### Settings & Accessibility

28. **Remappable Controls**: Full key/button remapping. Toggle options for hold-to-fire vs tap-to-fire. Optional autofire (setting or purchasable upgrade).
29. **Visual Accessibility**: Colorblind-friendly palette option. Adjustable screen shake (off/low/medium).
30. **Difficulty Presets** (optional): Casual / Classic / Hard. Affects enemy frequency, damage, and currency economy.

### Audio

31. **Sound Effects**: Distinct cues for fire, hit/damage, explosion (by asteroid size), pickup collect, shop purchase, and level clear. Immediate, satisfying feedback.
32. **Background Music** (optional): Minimal/ambient/retro synth. Must not fatigue over repeated runs.
33. **Volume Controls**: Separate sliders for master, music, and SFX.

## Non-Functional Requirements

- **Performance**: Smooth, consistent frame rate (target 60fps minimum) with no input lag. Gameplay must feel responsive at all times, even during intense combat with many on-screen entities (asteroids, enemies, projectiles, pickups).
- **Security**: No network access, no accounts, no data collection. All data stays local. No attack surface beyond the local filesystem.
- **Scalability**: Not applicable — single-player, single-machine, offline game. The only scaling concern is on-screen entity count during late-game levels.
- **Availability**: The game must launch and run reliably on the target platform without external dependencies at runtime. Settings and high scores persist across sessions via local storage.
- **Compatibility**: Must run on modern macOS (primary target, given the Asterax heritage). Cross-platform support (Windows, Linux) is desirable but not required for v1.0.

## Requirements Solution

The solution is a standalone, offline arcade space shooter built with original assets and branding. The game implements the classic Asteroids-style gameplay loop with the distinctive Asterax addition of between-level currency-based upgrades.

The core experience is a single-player endless run: the player pilots a ship through increasingly difficult levels of asteroids and enemy ships, collecting currency from destroyed asteroids, then spending that currency in a fly-through shop between levels. The shop offers upgrades across weapons, defense, mobility, economy, and repairs, plus an insurance system that lets players protect their upgrades against death. Each run ends when shields reach zero, and the player's score is recorded on a persistent local leaderboard.

The game prioritises feel and replayability over feature breadth. Physics are inertial and predictable. Difficulty scales smoothly through asteroid density, speed, and enemy escalation. The shop creates meaningful decisions each run without overwhelming the player. Every run starts completely fresh — no meta-progression, no persistent unlocks.

Visual direction is high-contrast retro arcade: dark backgrounds, bright ships and projectiles, satisfying explosion effects. Audio provides immediate feedback for every player action. The entire experience is designed to be picked up in seconds and replayed for hours.

## Application Logic

### Game State Machine

The application operates as a state machine with the following primary states:

1. **Main Menu** -> Player selects New Game, How to Play, Settings, High Scores, or Quit.
2. **Game Init** -> Ship class selection (if implemented), difficulty selection (if implemented), initialize fresh run state (zero currency, base stats, full shields).
3. **Combat Phase** -> Active gameplay. Player controls ship, destroys asteroids and enemies, collects currency. Runs until all asteroids/enemies for the level are cleared.
4. **Shop Phase** -> Between-level shop. Player flies ship through floating upgrade nodes to purchase. Timer optional. Transitions to next combat phase on player action or timeout.
5. **Game Over** -> Triggered when shields/hull reach zero during combat. Displays run summary. Prompts for high score entry if qualified. Returns to Main Menu.
6. **Pause** -> Overlays on combat or shop. Freezes all game logic. Offers resume, restart, settings, exit.

### Combat Phase Logic

- Asteroids spawn at level start based on difficulty parameters (count, size mix, speed range).
- Enemy ships spawn on a timer or trigger after early levels, escalating with level number.
- The player's ship responds to input with rotational and thrust forces applied to a velocity vector (inertial model).
- Projectiles are spawned at the ship's position/heading, travel at fixed speed, and expire after a set distance or time.
- Collision detection runs continuously: ship-asteroid, ship-enemy, ship-enemy-projectile, player-projectile-asteroid, player-projectile-enemy.
- On asteroid destruction: split into smaller asteroids (if not smallest), award points, roll for currency drop.
- On enemy destruction: award points, roll for currency/pickup drop.
- On ship damage: reduce shields/hull, play feedback effects, check for game over.
- All entities wrap at playfield edges.

### Shop Phase Logic

- Shop nodes are placed in a spatial layout (circle, grid, or thematic arrangement).
- Each node represents an upgrade category or specific item.
- When the ship collides with a node: check if player can afford it, deduct currency, apply upgrade, play purchase feedback, re-center ship.
- Insurance is a special node: purchasing it sets an insurance flag and deducts a recurring cost at each subsequent level transition.
- The shop phase ends on explicit player action (e.g., fly to "Continue" node) or optional timer.

### Persistence Logic

- High scores: stored locally (file or lightweight local database). Loaded at startup, written after each qualifying game over.
- Settings: stored locally. Loaded at startup, written on change.
- No run state persists across application launches — every launch starts fresh.

## Constraints

- **Technical**: Must use original assets only (no copied art, audio, fonts, or logos from Asterax or any other game). Tech stack to be determined by Solutions Architect, but must support 2D rendering with smooth physics at 60fps, local file persistence, and keyboard input handling.
- **Timeline**: No hard deadline specified. Quality and completeness take priority over speed.
- **Budget**: No monetary budget specified. This is a self-contained development project with no external service costs (no servers, no APIs, no licensed assets).
- **Team**: AI-assisted development. The team consists of AI agents coordinated by a human lead. No dedicated art or audio specialists — assets must be procedurally generated or created within the development process.
- **Legal**: Must avoid trademark confusion with "Asterax" or any other existing game title. All assets must be original. The shipped product name must be entirely new.

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| "Feel" is wrong — ship handling doesn't match player expectations | High | Medium | Early prototype of ship physics; playtest feedback loop before building full game |
| Difficulty curve is too steep or too flat | Medium | Medium | Parameterize difficulty scaling; playtest across skill levels; expose difficulty presets |
| Shop interaction (fly-through) is confusing or frustrating | High | Medium | Prototype shop UX early; ensure clear visual/audio feedback; consider fallback to menu-based shop if fly-through doesn't work |
| Asset quality (procedural/AI-generated) looks or sounds amateurish | Medium | Medium | Lean into retro-minimalist aesthetic where simpler assets are a feature, not a limitation |
| Scope creep from optional features | Medium | High | Clearly separate must-have from optional in phased delivery; defer all "optional" items to post-v1.0 unless trivial to include |
| Insurance system creates balance problems | Medium | Medium | Playtest insurance tiers; tune pricing to prevent trivializing difficulty |

## Assumptions

- The primary target platform is macOS, given the Asterax heritage and the development environment. The Solutions Architect may recommend a cross-platform technology.
- Keyboard is the primary input method. Gamepad support is desirable but not required for v1.0.
- "Retro" visual style means the game does not require high-fidelity 3D rendering or complex animations — 2D sprites or vector-style graphics are appropriate.
- The insurance system will require careful balance tuning, which may happen iteratively after initial implementation.
- Sound effects and music can be synthesized/procedural or sourced from royalty-free libraries, as long as they are legally clean.

## Out of Scope (v1.0)

- Online features: accounts, cloud saves, online matchmaking, online leaderboards.
- Multiplayer: co-op and versus modes are deferred to a future release.
- Monetization: ads, in-app purchases, subscriptions.
- Narrative campaign or cutscenes.
- Modding support.
- Meta-progression: no persistent unlocks, cosmetics, or cross-run progression.
- Mobile platforms.

## Resolved Design Decisions

The following questions from the requirements document (Section 23) have been resolved by the project stakeholder:

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Product name | New original title required. No reference to "Asterax" in the shipped product. | Avoid trademark risk; establish independent brand identity. |
| 2 | Multiplayer scope | Single player only for v1.0. | Reduce scope and architectural complexity for initial release. |
| 3 | Survival model | Shields-only (single health bar). Run ends when shields/hull hit zero. | Simpler, more modern feel. Removes extra lives complexity. |
| 4 | Insurance feature | Included in v1.0 as part of the shop. | Core to the Asterax-like experience; adds strategic depth to the shop. |
| 5 | Meta-progression | None. Pure arcade — every run starts completely fresh. | Preserves classic arcade identity; simplifies persistence layer. |

## Success Criteria

- [ ] A player can complete the full loop: start -> play multiple levels -> shop -> die -> record high score -> restart, with no blockers.
- [ ] Ship handling feels inertial, responsive, and predictable (Asteroids-family physics).
- [ ] Wrap-around playfield works correctly for ship, asteroids, and projectiles.
- [ ] Three-size asteroid splitting works correctly.
- [ ] Currency drops spawn, are visually distinct, and can be collected.
- [ ] Between-level shop is functional: player can fly through nodes to purchase upgrades.
- [ ] Insurance system is purchasable and correctly retains upgrades on death according to tier.
- [ ] Difficulty progression is coherent for at least 30 minutes of skilled play.
- [ ] UI is fully usable without a manual: controls in "How to Play", shop effects understandable, clear damage/pickup/purchase feedback.
- [ ] High scores and settings persist locally across application restarts.
- [ ] The game runs at a stable 60fps during normal and intense gameplay.
- [ ] All assets are original — no copied art, audio, or branding.

## Open Questions

1. **Product Name**: A new original title is required. Candidate names to consider (to be finalized before shipping):
   - **Voidbreaker** — evokes space destruction, original, no trademark conflicts apparent.
   - **Shardstorm** — references asteroid fragments ("shards") and the chaotic combat.
   - **Drift & Ruin** — captures the inertial physics ("drift") and escalating destruction.
   - Name finalization should occur before any public-facing assets (splash screen, icon, store listing) are created.

2. **Target Platform Specifics**: macOS is the primary target. Should the Solutions Architect plan for cross-platform from the start (e.g., via a cross-platform engine), or build macOS-first and port later?

## Approval

- [x] Reviewed by: Project Stakeholder
- [x] Approved on: 2026-02-18
