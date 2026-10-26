# 🧟‍♂️ Zombie Quarantine FPS: Project Breakout

A mobile-ready, retro 2.5D Raycasting First-Person Shooter set in a post-apocalyptic zombie quarantine zone, built with Python, Pygame-CE, and cloud integration with **Firebase** and **Supabase**.

Inspired by classic DOOM/Wolfenstein raycasting engines and adapted for modern mobile touchscreen devices with virtual joysticks, touch-look panning, and cloud telemetry.

---

## 📖 Story & Lore

A mutated biological pathogen leaked from BioCorp's underground Hive research facility has collapsed civilian society in hours. You play as **Sergeant Vance**, an elite soldier operating deep in high-hazard quarantine sectors. 

Your mission: Infiltrate five quarantine zones, eliminate zombie swarms, locate and rescue 1 trapped specialist survivor per level, and escort them to safety at the designated evacuation extraction point.

---

## 🎮 Campaign Levels & VIP Survivors

| Level | Sector Name | Locked Access Gate | VIP Survivor | Role & Intel |
| :--- | :--- | :--- | :--- | :--- |
| **Level 1** | **Outpost Medical Bay** | Red Medical Keycard | **Dr. Sarah Chen** | Field Doctor carrying viral incubation data |
| **Level 2** | **Abandoned Subway System** | Yellow Transit Keycard | **Marcus Vance** | Electrical Engineer with transit power bypass access |
| **Level 3** | **City Center Barricade** | Blue Tactical Keycard | **Sergeant Ramos** | Military Recon Scout with horde telemetry maps |
| **Level 4** | **Industrial Chemical Plant** | Green HAZMAT Keycard | **Dr. Elena Rostova** | Virology Specialist with live pathogen samples |
| **Level 5** | **Sub-level Research Lab** | Purple Master Keycard | **Dr. Arthur Sterling** | Head BioCorp Scientist with the Master Antidote |
| **Level 6** | **Bio-Dome Hydroponics** | Orange Botanical Keycard | **Dr. Maya Lin** | Botanist Specialist with cellular pathogen inhibitor |
| **Level 7** | **Underground Catacombs** | Crimson Heavy Keycard | **Chief Alvarez** | Demolitions Expert arming the hive blast detonator |
| **Level 8** | **Surface Airbase Evac** | Gold Master Keycard | **Major Katherine Ross** | Air Commander clearing heavy air extraction transport |

---

## 🎲 Procedural Random Map Generator Mode

The game features an integrated **BFS-Validated Procedural Map Generator** (`engine/map_generator.py`):
- **Dynamic Solvable Mazes**: Procedurally carves interconnected rooms and corridors, verified using graph Breadth-First Search (BFS) to guarantee a solvable path:
  1. `Player Start -> Keycard Pickup` (accessible without crossing locked gate)
  2. `Keycard -> Locked Security Door`
  3. `Door -> VIP Survivor Chamber`
  4. `Survivor -> Extraction Evacuation Bay`
- **Dynamic Difficulty Swarms**: Adjusts zombie density and infected classes (Walkers, Runners, Spitters, Brutes) scaled by sector hazard tier.
- **Dynamic Item Distribution**: Spawns Medkits, Ammo Crates, Kevlar Armor, Frag Grenades, and Adrenaline Stims across unexplored sectors.
- **Mode Toggle**: In the Lobby Menu, toggle between **Classic Campaign** and **Procedural Random** via the `[TOGGLE MODE]` button or key `R`, or click `[⚡ RANDOM MAP]` to instantly deploy into a unique layout!

---

## 🛠️ Architecture & Project Structure

```
c:\coding\game\
├── assets/
│   ├── textures/             # Raycast wall & door textures (Medical, Subway, Barricade, Plant, Lab, Doors, Evac)
│   ├── sprites/
│   │   ├── zombies/          # 2.5D Animated Sprites: Walker, Runner, Spitter, Brute (Idle, Walk, Attack, Death)
│   │   ├── survivors/        # 5 VIP Survivors: Doctor, Engineer, Scout, Virologist, Scientist
│   │   ├── weapons/          # First-person viewmodels: Shotgun, Assault Rifle, Tactical 9mm Pistol
│   │   └── pickups/          # Medkits, Ammo Boxes, Armor Vests, Color-coded Keycards, Grenades, Adrenaline
│   ├── ui/                   # Crosshair, HUD icons, Presplash, Touch controls
│   └── sound/                # 18 synthesized 8-bit / retro WAV sound effects
├── backend/
│   ├── supabase_service.py   # REST API for Global Leaderboards, User Profiles, and Rescue Badges
│   └── firebase_service.py   # Firebase Auth (Anonymous / Email) & Realtime DB progression sync
├── engine/
│   ├── settings.py           # Resolution (1280x720), FOV, Raycast math, weapon configs, level data
│   ├── sound_engine.py       # Pygame mixer & mathematical wave synthesis for 8-bit audio
│   ├── asset_manager.py      # Asset pipeline & procedural texture/sprite generator
│   ├── raycasting.py         # DDA Raycaster with wall slice projection and distance shading
│   ├── object_renderer.py    # Compositor for parallax skybox, floor, walls, sprites, and blood damage
│   ├── map_engine.py         # 5 campaign level maze grids, doors, keycards, pickups, extraction gates
│   ├── player.py             # First-person movement, wall sliding, health, armor absorption, interactions
│   ├── weapons.py            # Hitscan ballistics, ammo management, grenade physics, medkits, adrenaline
│   ├── npcs.py               # Zombie swarm AI, pathfinding pursuit, survivor NPC logic, 2.5D projections
│   ├── pathfinding.py        # BFS shortest-path maze navigation for zombie AI
│   └── touch_controls.py     # Mobile Virtual Joystick, Touch-Look Panning, and Action Buttons
├── ui/
│   ├── hud.py                # Mobile HUD: Health/Armor bars, ammo, radar minimap, objective tracker
│   ├── lobby_menu.py         # Main Menu: Level Selector (1-5), Armory Loadout, Operative Stats, Leaderboard
│   └── dialogs.py            # Mission Victory Debriefing & Game Over modals
├── backend_config.json       # Live Supabase & Firebase API keys template
├── buildozer.spec            # Android APK packaging configuration (Python-for-Android / Pygame-CE)
├── main.py                   # Main game entrypoint
└── requirements.txt          # Python dependencies
```

---

## 📱 Mobile Controls & Desktop Fallback

### Mobile Touchscreen Interface:
- **Virtual Joystick (Bottom Left):** Smooth 360-degree analog thumbstick for walking and strafing.
- **Touch-Look Panning (Right Screen):** Swipe anywhere on the right half of the screen to pan your viewpoint smoothly.
- **Action Buttons (Bottom Right):**
  - **FIRE (Red):** Shoots current equipped weapon.
  - **RELOAD (Amber):** Reloads weapon clip from reserves.
  - **SWITCH (Cyan):** Cycles between Pistol, Shotgun, and Assault Rifle.
  - **ACTION / RESCUE (Green):** Contextual button that lights up when near doors (to swipe keycards), near survivors (to rescue), or at the evacuation gate.
  - **FRAG (Orange):** Throws a timed M67 Frag Grenade.
  - **HEAL (Teal):** Uses a Trauma Medkit (+50 HP).

### Desktop Keyboard / Mouse Controls:
- **Move:** `W`, `A`, `S`, `D` or `Arrow Keys`
- **Shoot:** `Space` or `Left Mouse Click`
- **Reload:** `R`
- **Interact / Rescue / Unlock:** `E`
- **Switch Weapons:** `1` (Pistol), `2` (Shotgun), `3` (Rifle)
- **Frag Grenade:** `G`
- **Trauma Medkit:** `H`
- **Adrenaline Stim:** `Q`
- **Toggle Mouse Look:** `Tab` or `M`
- **Pause / Return to Lobby:** `ESC`

---

## 🔫 Weapons & Tactical Equipment

### Weapons:
1. **Combat 12G Shotgun:** 9-pellet spread buckshot. Devastating close-range burst damage (198 max damage per blast).
2. **M4A1 Assault Rifle:** High-velocity 3-round burst mode (75ms intra-burst fire rate). Rapid precision suppression for long-range swarm defense.
3. **Tactical 9mm Pistol:** Pinpoint accuracy sidearm with rapid mobility and ammo conservation.

### Tactical Equipment:
1. **Trauma Medkit:** Instantly heals 50 HP.
2. **M67 Frag Grenade:** Raycast area-of-effect explosive dealing up to 140 damage in adjacent grid tiles.
3. **Kevlar Armor Vest:** Passively absorbs 40% of all incoming damage from zombies until depleted.
4. **Adrenaline Stim Shot:** Injects pure epinephrine for +45% movement speed for 10 seconds.

---

## ☁️ Cloud Backend Integration (Firebase & Supabase)

### 1. Supabase Integration:
- **Leaderboards:** Records fastest level clearance times, username, and zombie kill count.
- **Rescue Badges:** Awards and records unique campaign honor badges for extracting each of the 5 survivors:
  - *Caduceus Badge* (Field Doctor)
  - *Circuit Breaker* (Electrical Engineer)
  - *Pathfinder Star* (Military Scout)
  - *Antidote Harvester* (Virology Specialist)
  - *Apocalypse Savior* (Head Scientist)
- **Offline Fallback:** When running offline or before setting keys, a built-in local cache (`supabase_local_cache.json`) provides seamless offline rankings and records.

### 2. Firebase Integration:
- **Firebase Auth:** Supports anonymous guest authentication and email/password accounts.
- **Realtime DB / Firestore:** Automatically syncs unlocked levels, selected weapon loadouts, currency balance, and career statistics to the cloud (`firebase_local_cache.json`).

To connect your live cloud instances, populate `backend_config.json`:
```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_key": "your-anon-key-here",
  "firebase_api_key": "your-firebase-web-api-key-here",
  "firebase_db_url": "https://your-firebase-project-default-rtdb.firebaseio.com"
}
```

---

## 🚀 How to Run Locally

### Requirements:
- Python 3.10+
- `pygame-ce` (Pygame Community Edition)
- `pillow`

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py

# Run automated integration tests
python test_gameplay.py
```

---

## 📱 Building the Android APK

The project includes a pre-configured `buildozer.spec` optimized for Android deployment via Pygame-CE and Python-for-Android (SDL2 bootstrap).

```bash
# Install buildozer and dependencies on Linux / WSL / GitHub Actions
pip install buildozer cython virtualenv

# Build Android APK in debug mode
buildozer android debug

# The compiled APK will be generated under:
# bin/quarantine_breakout-1.0.0-arm64-v8a-debug.apk
```
