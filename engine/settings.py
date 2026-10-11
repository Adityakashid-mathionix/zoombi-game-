"""
Global settings, constants, and configuration for Zombie Quarantine FPS Mobile Engine.
"""
import math

# Screen & Display Settings (Mobile 16:9 Landscape)
RES = WIDTH, HEIGHT = 1280, 720
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 60

# Raycasting Engine Parameters
FOV = math.pi / 3  # 60 degrees Field of View
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2  # 640 rays for crisp resolution & smooth mobile performance
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 24  # Max ray distance in grid units
SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

# Player Movement & Controls
PLAYER_POS = (2.5, 2.5)
PLAYER_ANGLE = 0.0
PLAYER_SPEED = 0.0035  # Units per millisecond
PLAYER_ROT_SPEED = 0.0024  # Radians per millisecond
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_ARMOR = 100

# Touch & Mouse Controls Sensitivity
TOUCH_LOOK_SENSITIVITY = 0.0032
MOUSE_SENSITIVITY = 0.0025
JOYSTICK_RADIUS = 75
JOYSTICK_DEADZONE = 12
BUTTON_RADIUS = 36

# Audio & Volume
SOUND_VOLUME = 0.8
MUSIC_VOLUME = 0.5

# Visual Theme Colors
COLOR_BLACK = (10, 10, 12)
COLOR_DARK_GRAY = (28, 28, 35)
COLOR_FLOOR = (24, 24, 30)
COLOR_CEILING = (16, 16, 22)
COLOR_WHITE = (245, 245, 250)
COLOR_BLOOD = (220, 20, 30)
COLOR_AMBER = (255, 175, 40)
COLOR_GREEN = (45, 215, 95)
COLOR_CYAN = (0, 210, 255)
COLOR_PURPLE = (180, 70, 240)
COLOR_YELLOW = (250, 220, 30)

# Campaign Levels Definition
LEVELS_DATA = {
    1: {
        "title": "Level 1: Outpost Medical Bay",
        "subtitle": "Quarantine Zone Alpha",
        "survivor": "Field Doctor",
        "survivor_name": "Dr. Sarah Chen",
        "survivor_bio": "Chief triage physician with viral transmission data.",
        "keycard_name": "Red Medical Keycard",
        "keycard_color": (230, 45, 55),
        "theme": "medical",
        "floor_color": (32, 38, 42),
        "ceiling_color": (18, 22, 26),
        "ambient_light": 0.85,
    },
    2: {
        "title": "Level 2: Abandoned Subway System",
        "subtitle": "Metro Line 4 Tunnels",
        "survivor": "Electrical Engineer",
        "survivor_name": "Marcus Vance",
        "survivor_bio": "Power grid specialist with city transit bypass access.",
        "keycard_name": "Yellow Transit Keycard",
        "keycard_color": (245, 200, 35),
        "theme": "subway",
        "floor_color": (25, 24, 22),
        "ceiling_color": (15, 14, 13),
        "ambient_light": 0.70,
    },
    3: {
        "title": "Level 3: City Center Barricade",
        "subtitle": "Downtown Checkpoint Omega",
        "survivor": "Military Scout",
        "survivor_name": "Sergeant Ramos",
        "survivor_bio": "Recon scout with zombie horde telemetry & air route maps.",
        "keycard_name": "Blue Tactical Keycard",
        "keycard_color": (35, 145, 245),
        "theme": "barricade",
        "floor_color": (28, 28, 30),
        "ceiling_color": (20, 18, 24),
        "ambient_light": 0.80,
    },
    4: {
        "title": "Level 4: Industrial Chemical Plant",
        "subtitle": "BioCorp Petrochemical Facility",
        "survivor": "Virology Specialist",
        "survivor_name": "Dr. Elena Rostova",
        "survivor_bio": "Lead vaccine researcher carrying mutated pathogen samples.",
        "keycard_name": "Green HAZMAT Keycard",
        "keycard_color": (45, 220, 80),
        "theme": "chemical",
        "floor_color": (22, 32, 24),
        "ceiling_color": (14, 20, 16),
        "ambient_light": 0.75,
    },
    5: {
        "title": "Level 5: Sub-level Research Lab",
        "subtitle": "BioCorp Hive - Sub Level -4",
        "survivor": "Head Scientist",
        "survivor_name": "Dr. Arthur Sterling",
        "survivor_bio": "Facility director holding the Master Dispersal Antidote.",
        "keycard_name": "Purple Master Keycard",
        "keycard_color": (190, 60, 245),
        "theme": "lab",
        "floor_color": (20, 24, 32),
        "ceiling_color": (12, 16, 22),
        "ambient_light": 0.80,
    }
}

# Weapons Definitions
WEAPON_CONFIGS = {
    "pistol": {
        "name": "Tactical 9mm Pistol",
        "damage": 34,
        "fire_rate_ms": 320,
        "max_ammo": 12,
        "reserve_ammo": 72,
        "reload_time_ms": 1100,
        "pellets": 1,
        "spread": 0.015,
        "icon": "pistol_icon",
    },
    "shotgun": {
        "name": "Combat 12G Shotgun",
        "damage": 18,  # per pellet
        "fire_rate_ms": 780,
        "max_ammo": 6,
        "reserve_ammo": 36,
        "reload_time_ms": 1700,
        "pellets": 7,
        "spread": 0.08,
        "icon": "shotgun_icon",
    },
    "rifle": {
        "name": "M4A1 Assault Rifle",
        "damage": 28,
        "fire_rate_ms": 130,  # Rapid automatic
        "max_ammo": 30,
        "reserve_ammo": 180,
        "reload_time_ms": 1400,
        "pellets": 1,
        "spread": 0.035,
        "icon": "rifle_icon",
    }
}

# Tactical Equipment
TACTICAL_CONFIGS = {
    "medkit": {
        "name": "Trauma Medkit",
        "description": "Restores 50 HP immediately.",
        "heal_amount": 50,
        "max_capacity": 5,
    },
    "grenade": {
        "name": "M67 Frag Grenade",
        "description": "Explosive raycast AoE blast damaging all entities within 2.5 grid tiles.",
        "damage": 140,
        "radius": 2.5,
        "fuse_time_ms": 1400,
        "max_capacity": 5,
    },
    "armor_vest": {
        "name": "Tactical Kevlar Vest",
        "description": "Reduces incoming zombie damage by 40%.",
        "damage_reduction": 0.40,
        "armor_points": 100,
    },
    "adrenaline": {
        "name": "Adrenaline Stim Shot",
        "description": "Temporarily increases movement speed by 45% for 10 seconds.",
        "duration_ms": 10000,
        "speed_multiplier": 1.45,
        "max_capacity": 3,
    }
}
