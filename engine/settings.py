"""
Global settings, constants, and configuration for Zombie Quarantine FPS Mobile Engine.
"""
import math

# Screen & Display Settings (Mobile 16:9 Landscape)
RES = WIDTH, HEIGHT = 1280, 720
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 0  # Uncapped buttery-smooth frame pacing like reference DOOM

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

# Player Movement & Controls (Synchronized with Reference DOOM Physics)
PLAYER_POS = (2.5, 2.5)
PLAYER_ANGLE = 0.0
PLAYER_SPEED = 0.004  # Units per millisecond (exact reference DOOM speed)
PLAYER_RUN_SPEED = 0.0065  # Sprint speed when holding Shift or pushing virtual joystick
PLAYER_ROT_SPEED = 0.002  # Radians per millisecond (exact reference DOOM rot speed)
PLAYER_SIZE_SCALE = 60  # Wall collision projection scale
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_ARMOR = 100

# Touch & Mouse Controls Sensitivity (Exact Reference DOOM Parameters)
TOUCH_LOOK_SENSITIVITY = 0.0032
MOUSE_SENSITIVITY = 0.0003  # Scaled by delta_time
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT
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
COLOR_ORANGE = (255, 130, 25)
COLOR_CRIMSON = (220, 25, 45)
COLOR_GOLD = (245, 215, 30)

# Campaign Levels Definition
LEVELS_DATA = {
    1: {
        "title": "Level 1: Outpost Medical Bay",
        "subtitle": "Quarantine Zone Alpha",
        "survivor": "Engineer Shlok",
        "survivor_name": "Shlok 'CR'",
        "survivor_bio": "Lead systems engineer nicknamed 'CR', barricaded in quarantine holding override keys.",
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
        "survivor": "Miss Rakhi",
        "survivor_name": "Miss Rakhi",
        "survivor_bio": "Terrified survivor trapped in the subway security sector, desperately seeking escape.",
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
        "survivor": "Jethalal Gada",
        "survivor_name": "Jethalal Gada",
        "survivor_bio": "Beloved proprietor of Gada Electronics, terrified and trapped behind the barricade.",
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
    },
    6: {
        "title": "Level 6: Bio-Dome Hydroponics",
        "subtitle": "Sector 7 Greenhouse Complex",
        "survivor": "Papu",
        "survivor_name": "Papu",
        "survivor_bio": "VIP Survivor holding the bio-dome botanical cellular pathogen inhibitor.",
        "keycard_name": "Orange Botanical Keycard",
        "keycard_color": (255, 130, 25),
        "theme": "greenhouse",
        "floor_color": (24, 34, 26),
        "ceiling_color": (15, 22, 17),
        "ambient_light": 0.85,
    },
    7: {
        "title": "Level 7: Underground Catacombs & Vaults",
        "subtitle": "Subterranean Cold War Bunker",
        "survivor": "Panditji Maharaj",
        "survivor_name": "Panditji Maharaj",
        "survivor_bio": "Holy spiritual ascetic holding ancient catacomb vault sanctification secrets.",
        "keycard_name": "Crimson Temple Keycard",
        "keycard_color": (220, 25, 45),
        "theme": "catacombs",
        "floor_color": (22, 20, 24),
        "ceiling_color": (14, 12, 16),
        "ambient_light": 0.70,
    },
    8: {
        "title": "Level 8: Surface Airbase Evac",
        "subtitle": "Sector Zero Final Runway",
        "survivor": "Modinho",
        "survivor_name": "Modinho",
        "survivor_bio": "Supreme leader Modinho awaiting total airbase extraction with blessings and victory.",
        "keycard_name": "Gold Master Keycard",
        "keycard_color": (245, 215, 30),
        "theme": "airbase",
        "floor_color": (26, 28, 32),
        "ceiling_color": (16, 18, 22),
        "ambient_light": 0.85,
    },
}

# Weapons Definitions
WEAPON_CONFIGS = {
    "pistol": {
        "name": "Tactical 9mm Pistol",
        "damage": 14,
        "fire_rate_ms": 280,
        "max_ammo": 12,
        "reserve_ammo": 72,
        "reload_time_ms": 1100,
        "pellets": 1,
        "spread": 0.015,
        "range": 8.5,
        "effective_range": 5.0,
        "range_label": "Medium (8.5m)",
        "damage_label": "Low",
        "icon": "pistol_icon",
    },
    "shotgun": {
        "name": "Combat 12G Shotgun",
        "damage": 22,  # per pellet (9 pellets = 198 point-blank burst damage)
        "fire_rate_ms": 480,
        "max_ammo": 2,  # 2-shell double-barrel / breach reload
        "reserve_ammo": 32,
        "reload_time_ms": 1300,
        "pellets": 9,
        "spread": 0.085,
        "range": 4.5,
        "effective_range": 2.2,
        "range_label": "Short (4.5m)",
        "damage_label": "High",
        "icon": "shotgun_icon",
    },
    "rifle": {
        "name": "M4A1 Assault Rifle",
        "damage": 26,
        "fire_rate_ms": 75,   # Rapid 75ms intra-burst cadence
        "burst_count": 3,     # 3-round burst fire mode
        "burst_delay_ms": 190,# Delay between consecutive 3-round bursts
        "max_ammo": 30,
        "reserve_ammo": 180,
        "reload_time_ms": 1350,
        "pellets": 1,
        "spread": 0.025,
        "range": 16.0,
        "effective_range": 12.0,
        "range_label": "Long (16m)",
        "damage_label": "Medium",
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


def safe_font(size, bold=False):
    """Safely loads font with universal Android fallback to prevent crashes."""
    import pygame as _pg
    if not _pg.font.get_init():
        try:
            _pg.font.init()
        except Exception:
            pass
    try:
        f = _pg.font.SysFont("Arial", size, bold=bold)
        if f is not None:
            return f
    except Exception:
        pass
    try:
        return _pg.font.Font(None, size)
    except Exception:
        return None

