# requirements.md — Local “Asterax”-Style Retro Space Shooter (Business Requirements)
Version: 1.0  
Date: 2026-02-17  
Status: Draft for scoping into technical design later

## 1. Purpose
Create an entirely local, offline, playable game that replicates the core *feel* of the classic Mac game **Asterax**: an Asteroids-like arcade space shooter with an in-run currency used to purchase upgrades and score bonuses between levels, escalating difficulty, and fast “one more run” replayability.

This document is **non-technical** and focuses on design, gameplay, levels, and player-facing functionality.

## 2. Guiding Principles
1. **Faithful feel first**: movement, shooting, collisions, and pacing should evoke the original.
2. **Offline by default**: the full experience must work with no internet connection and no accounts.
3. **Clarity over complexity**: minimal friction to start playing; easy to learn, hard to master.
4. **Skill + choices**: player success depends on both piloting skill and upgrade decisions.
5. **Modern convenience without changing the core loop**: quality-of-life is allowed if it doesn’t alter the fundamental gameplay identity.

## 3. Legal / IP Guardrails (Non-Negotiable)
To keep this project safe to distribute:
- Use **original** visuals, audio, UI assets, and branding.
- Do **not** copy original art, sound effects, fonts, logos, or any proprietary content.
- Avoid using the original game’s name in shipping product branding if it risks trademark confusion.
- The goal is a **spiritual successor / faithful gameplay clone**, not a 1:1 asset recreation.

## 4. Target Audience
- Players who enjoyed classic Mac shareware/arcade shooters.
- Players who like Asteroids-style physics, score chasing, and upgrade-driven runs.
- Local couch players (if multiplayer is included).

## 5. Supported Play Styles
### 5.1 Single Player (Core)
A run-based arcade loop of:
**Fight → Collect currency → Shop/upgrade → Next level → Repeat until death → High score**

### 5.2 Local Multiplayer (Strongly Desired)
- Local play on the same machine.
- Modes:
  - **Co-op**: survive together; shared or separate currency (configurable).
  - **Versus**: score race or “last ship standing”.
- Multiplayer must preserve readability and fairness (no chaotic UI).

## 6. Core Game Loop
### 6.1 Level Structure
Each level is composed of:
1. **Combat Phase**: asteroids + escalating threats.
2. **Pickup Phase**: currency drops to collect under pressure.
3. **Transition / Shop Phase**: buy upgrades, repairs, and score bonuses.
4. **Next Level**: difficulty increases.

### 6.2 Win/Loss Condition
- The game is primarily **endless** (no final “campaign end” required).
- A “run” ends when the player’s survival resource is exhausted (e.g., shields/hull/lives).
- Success is measured by **score**, **levels cleared**, and optional **milestones**.

## 7. Player Ship & Controls
### 7.1 Core Controls (Minimum)
- Rotate left/right
- Thrust/accelerate
- Fire primary weapon
- Optional: brake/retro-thrust (if consistent with feel)
- Optional: special weapon/ability (if purchased)

### 7.2 Handling & Physics Feel
- 2D top-down space movement with **inertia**.
- “Arcade readable” physics: responsive, predictable, and learnable.
- Optional ship “classes” (recommended):
  - **Nimble**: faster turning, lower durability
  - **Tank**: slower, higher durability
  - **Balanced**: middle ground

### 7.3 Screen/Playfield Behavior
- The playfield **wraps**: exiting one edge re-enters from the opposite edge.
- The ship, asteroids, and projectiles follow consistent wrap rules.

## 8. Combat Mechanics
### 8.1 Shooting
- Primary weapon fires projectiles with:
  - **Maximum range / lifetime** (shots disappear after traveling a distance/time).
  - Optional **on-screen projectile cap** (prevents infinite spam; encourages timing).
- Shooting feedback must be immediate and satisfying (sound + visual effect).

### 8.2 Collisions & Damage
- Colliding with asteroids or enemy fire causes damage.
- Clear feedback when taking damage (flash, sound, brief invulnerability optional).
- Friendly fire rules in multiplayer are configurable (on/off).

## 9. Asteroids (Primary Obstacle)
### 9.1 Sizes & Splitting
- Asteroids come in **three sizes** (large/medium/small).
- Destroying a larger asteroid splits it into multiple smaller asteroids.
- The smallest size is fully destructible (no further splitting).

### 9.2 Difficulty Scaling via Asteroids
Across levels, increase one or more of:
- Number of asteroids
- Asteroid speed / spin
- Spawn pressure (e.g., new asteroids introduced mid-level)
- Complexity (e.g., mixed sizes, denser fields)

## 10. Enemies (Secondary Threats)
### 10.1 Enemy UFOs / Ships
- Enemy ships appear after early levels and escalate over time.
- Enemies fire projectiles at the player(s).
- Different enemy archetypes (minimum set):
  - **Basic shooter**: slow, simple firing pattern
  - **Aggressive**: faster, higher rate of fire
  - **Sniper** (optional): slower cadence, higher accuracy
- Enemies must be readable and fair: strong telegraphs, avoid “cheap” deaths.

## 11. Currency & Pickups
### 11.1 Currency Drops (“Crystals” Equivalent)
- Destroyed asteroids have a **chance** to drop currency pickups.
- Currency pickups:
  - Must be **collected by contact** (fly over them).
  - Have a clear visual identity and “collect” sound.
  - May be lost if not collected in time (optional timeout).
- Optional “authentic feel” rule:
  - Currency pickups can be destroyed by stray shots unless the player buys an upgrade that prevents this.

### 11.2 Additional Pickups (Optional)
- Rare drops that provide:
  - Small heal/repair
  - Temporary shield
  - Temporary damage boost
  - Temporary speed boost

## 12. Shop / Upgrade Phase (Signature Feature)
### 12.1 Access & Timing
- Shop appears **between levels**.
- Player can spend currency on upgrades and bonuses before starting the next combat phase.
- Shop is fast to use (target: 5–20 seconds typical).

### 12.2 Shop Interaction Style (Desired “Asterax-like”)
- Player still controls the ship during the shop phase.
- Items/categories are represented as **floating nodes/orbs**; the player “flies into” a node to purchase.
- After purchasing, the ship returns to a neutral position (or is gently re-centered).
- Must clearly show:
  - Current currency
  - Item cost
  - Item effect (simple language)
  - Current upgrade level (if upgradable)

### 12.3 Upgrade Categories (Minimum)
1. **Weapons**
   - Fire rate
   - Damage
   - Projectile speed/range (if applicable)
   - Spread shot / multi-shot (optional)
2. **Defense**
   - Shields / armor
   - Damage reduction (optional)
3. **Mobility**
   - Thrust power
   - Turn rate
   - Drift control (optional)
4. **Economy / Utility**
   - Increased currency drop rate (optional, careful for balance)
   - Pickup magnet / attraction radius
   - “Currency can’t be destroyed by shots” (if using that rule)
5. **Repairs**
   - Restore shields/hull (no free heal between levels unless explicitly designed)

### 12.4 Score Bonuses (Optional but On-Brand)
- Purchasable score multipliers or bonuses that trade survivability for points.

### 12.5 Insurance (Optional “Classic-like” Feature)
- Player may buy an **insurance plan** that costs currency each level.
- If insured, the player retains some/all upgrades upon death (configurable):
  - Keep all upgrades (premium)
  - Keep a subset (basic)
  - Keep nothing (off)

## 13. Levels, Difficulty, and Progression
### 13.1 Difficulty Curve Goals
- Early levels teach fundamentals with low enemy pressure.
- Mid levels introduce enemy ships and force upgrade decisions.
- Late levels become intense but still “fair” (skill can carry).
- Difficulty must scale smoothly; no sudden impossible spikes.

### 13.2 Progression Model
- Primary progression is **in-run** (upgrades purchased during a run).
- Meta-progression is **optional** and should be minimal to preserve the classic arcade identity:
  - Cosmetic unlocks only (preferred), or
  - Optional “challenge modes”

### 13.3 Level Variety (Optional Enhancements)
If added, variety should not undermine clarity:
- Background themes (nebula, asteroid belt, deep space)
- Hazard variants (e.g., debris fields, mines) introduced gradually

## 14. Scoring & High Scores
### 14.1 Scoring Rules
- Points for destroying asteroids (scaled by size).
- Points for destroying enemies.
- Optional bonus for:
  - Clearing a level quickly
  - Not taking damage in a level
  - Collecting all currency drops (risky)

### 14.2 High Score Board (Local)
- Persistent local high score table:
  - Name/initials entry
  - Score
  - Level reached
  - Mode (single / co-op / versus)
  - Date/time (local)
- Separate leaderboards per mode/difficulty.

## 15. Game Modes (Detailed)
### 15.1 Classic Endless (Default)
- Standard rules, endless progression, local high scores.

### 15.2 Practice / Training (Recommended)
- Low-stakes sandbox for learning controls and mechanics.
- Toggle: asteroids only, no enemies, infinite shields (optional).

### 15.3 Challenge Variants (Optional)
- “No shop” survival
- “Double enemies”
- “Low visibility”
- Time attack (survive X minutes)

## 16. UI / UX Requirements
### 16.1 Main Menu
- New Game (single)
- Multiplayer (if enabled)
- How to Play
- Settings
- High Scores
- Quit

### 16.2 In-Game HUD (Minimum)
- Shields/hull (or lives)
- Current score
- Current level
- Currency amount
- Optional: weapon/upgrade indicators

### 16.3 Pause & Resume
- Pause must freeze action instantly.
- Pause menu options:
  - Resume
  - Restart run
  - Settings
  - Exit to menu

### 16.4 Game Over
- Show run summary:
  - Score, level reached, enemies destroyed, currency collected/spent
- If score qualifies, prompt for initials/name.

## 17. Visual Direction (Non-Technical)
- Readable, high-contrast retro aesthetic.
- Dark background with bright ships/projectiles/pickups.
- Effects should be “arcade satisfying”:
  - Explosions for asteroids and enemies
  - Pickup sparkle/flash for currency
  - Damage flash for ship

## 18. Audio Direction (Non-Technical)
- Distinct sound cues:
  - Fire
  - Hit/damage
  - Explosion by asteroid size
  - Pickup collect
  - Shop purchase
  - Level clear
- Optional looping background music:
  - Minimal/ambient/retro synth
  - Must not fatigue over repeated runs
- Volume sliders per channel (music, SFX, master).

## 19. Settings & Accessibility
### 19.1 Controls
- Remappable keys/buttons.
- Toggle options:
  - Hold-to-fire vs tap-to-fire (optional)
  - Autofire (optional; may be an upgrade or a setting)

### 19.2 Visual Accessibility
- Colorblind-friendly palette option.
- Adjustable screen shake (off/low/medium).

### 19.3 Difficulty Options (If Included)
- Difficulty presets (e.g., Casual / Classic / Hard).
- Difficulty affects enemy frequency, damage, and currency economy.

## 20. Local-Only Requirements
- No login, no cloud saves, no online multiplayer required.
- All persistence (settings, high scores) stored locally.
- The game remains playable with the machine fully offline.

## 21. Quality Bar / Acceptance Criteria (Player-Facing)
The project is considered ready for “v1.0 local release” when:
1. A player can complete the loop: **start → play multiple levels → shop → die → record high score → restart** with no blockers.
2. Core feel matches the reference pillars:
   - Inertial ship handling
   - Wrap-around playfield
   - Three-size asteroid splitting
   - Currency drops and collection
   - Between-level upgrade purchasing
3. Difficulty progression is coherent for at least **30 minutes** of skilled play.
4. UI is fully usable without a manual:
   - Controls discoverable in “How to Play”
   - Shop effects understandable
   - Clear feedback on damage, pickups, purchases
5. Local persistence works:
   - High scores and settings remain after closing and reopening the game.
6. If multiplayer is included:
   - Two players can start a session, complete levels, shop, and finish with a result screen.

## 22. Non-Goals (For This Spec)
- Online features (accounts, cloud, online matchmaking)
- Monetization (ads, IAP, subscriptions)
- Narrative campaign with cutscenes
- Modding support (can be future scope)

## 23. Open Questions (To Resolve Before Technical Design)
1. Should the shipped product name reference “Asterax” at all, or use a new title?
2. Multiplayer: co-op only, versus only, or both?
3. Run-ending rule: shields-only (no extra lives) vs classic lives system?
4. Insurance: included in v1.0 or deferred to a later release?
5. Meta-progression: none (pure arcade) vs light cosmetics?

---
End of requirements.md
