"""
Campaign Level Maps & Dynamic World Engine.
Features 5 distinct campaign levels, raycasted maze geometry, locked security doors,
item pickups, zombie spawn points, and extraction gates.
"""
from engine.settings import LEVELS_DATA


class LevelMap:
    def __init__(self, level_id):
        self.level_id = level_id
        self.meta = LEVELS_DATA.get(level_id, LEVELS_DATA[1])
        self.wall_type = level_id
        self.door_type = 100 + level_id
        self.ext_type = 99
        self.grid = []
        self.world_map = {}
        self.door_positions = {}
        self.player_start = (2.5, 2.5)
        self.survivor_pos = (12.5, 12.5)
        self.extraction_pos = (14.5, 14.5)
        self.pickups = []  # list of {"type": str, "pos": (x, y), "collected": False}
        self.zombie_spawns = []  # list of {"type": str, "pos": (x, y)}
        self.survivor_rescued = False
        self.extraction_unlocked = False

        self.build_level_geometry()

    def build_level_geometry(self):
        w = self.wall_type
        d = self.door_type
        e = self.ext_type
        _ = 0

        if self.level_id == 1:
            # Level 1: Outpost Medical Bay (Rescue: Field Doctor)
            # Layout: Triage Ward -> Central Clinic -> Locked Pharmacy (Keycard needed) -> Evac Bay
            self.grid = [
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
                [w, _, _, _, w, _, _, _, _, _, w, _, _, _, _, w],
                [w, _, _, _, w, _, w, w, w, _, w, _, w, w, _, w],
                [w, _, _, _, _, _, _, _, w, _, _, _, _, w, _, w],
                [w, w, _, w, w, w, _, _, w, w, w, w, _, w, _, w],
                [w, _, _, _, _, w, _, _, _, _, _, w, _, _, _, w],
                [w, _, w, w, _, w, _, w, w, _, _, w, w, w, _, w],
                [w, _, _, w, _, _, _, w, _, _, _, _, _, w, _, w],
                [w, w, _, w, w, w, _, w, _, w, w, w, _, w, _, w],
                [w, _, _, _, _, w, _, _, _, w, _, _, _, _, _, w],
                [w, _, w, w, _, w, w, d, w, w, _, w, w, w, _, w],
                [w, _, _, w, _, _, _, _, _, _, _, w, _, _, _, w],
                [w, w, _, w, _, w, w, _, w, w, _, w, _, e, _, w],
                [w, _, _, _, _, w, _, _, _, w, _, w, _, _, _, w],
                [w, _, w, w, w, w, _, _, _, w, _, _, _, _, _, w],
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
            ]
            self.player_start = (2.5, 2.5)
            self.survivor_pos = (7.5, 11.5)  # Safe room behind door (7, 10)
            self.extraction_pos = (13.5, 12.5)
            self.door_positions[(7, 10)] = {"locked": True, "required_keycard": "red", "open": False}

            self.pickups = [
                {"type": "keycard_red", "pos": (13.5, 2.5), "collected": False},
                {"type": "medkit", "pos": (1.5, 5.5), "collected": False},
                {"type": "medkit", "pos": (6.5, 11.5), "collected": False},
                {"type": "ammo", "pos": (9.5, 1.5), "collected": False},
                {"type": "ammo", "pos": (14.5, 7.5), "collected": False},
                {"type": "armor", "pos": (1.5, 13.5), "collected": False},
                {"type": "grenade", "pos": (10.5, 9.5), "collected": False},
            ]
            self.zombie_spawns = [
                {"type": "walker", "pos": (6.5, 3.5)},
                {"type": "walker", "pos": (9.5, 3.5)},
                {"type": "walker", "pos": (3.5, 7.5)},
                {"type": "runner", "pos": (12.5, 5.5)},
                {"type": "runner", "pos": (10.5, 7.5)},
                {"type": "walker", "pos": (1.5, 9.5)},
                {"type": "spitter", "pos": (13.5, 9.5)},
                {"type": "walker", "pos": (4.5, 13.5)},
                {"type": "runner", "pos": (10.5, 13.5)},
            ]

        elif self.level_id == 2:
            # Level 2: Abandoned Subway System (Rescue: Electrical Engineer)
            # Layout: Platform -> Dark Metro Rails -> High Voltage Substation (Yellow Keycard)
            self.grid = [
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
                [w, _, _, _, _, _, w, _, _, _, _, _, _, _, _, w],
                [w, _, w, w, w, _, w, _, w, w, w, w, w, w, _, w],
                [w, _, w, _, _, _, _, _, _, _, _, _, _, w, _, w],
                [w, _, w, _, w, w, w, w, w, _, w, w, _, w, _, w],
                [w, _, _, _, w, _, _, _, w, _, _, w, _, _, _, w],
                [w, w, w, _, w, _, w, _, w, w, _, w, w, w, _, w],
                [w, _, _, _, _, _, w, _, _, _, _, _, _, w, _, w],
                [w, _, w, w, w, w, w, _, w, w, w, w, _, w, _, w],
                [w, _, _, _, _, _, _, _, w, _, _, _, _, _, _, w],
                [w, w, w, w, _, w, w, w, w, _, w, w, w, w, _, w],
                [w, _, _, _, _, _, _, _, _, _, _, _, _, w, _, w],
                [w, _, w, w, w, w, w, d, w, w, w, w, _, w, _, w],
                [w, _, w, _, _, _, _, _, _, _, _, w, _, _, _, w],
                [w, _, _, _, w, _, _, _, _, w, _, _, _, e, _, w],
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
            ]
            self.player_start = (2.5, 2.5)
            self.survivor_pos = (7.5, 13.5)
            self.extraction_pos = (13.5, 14.5)
            self.door_positions[(7, 12)] = {"locked": True, "required_keycard": "yellow", "open": False}

            self.pickups = [
                {"type": "keycard_yellow", "pos": (14.5, 3.5), "collected": False},
                {"type": "medkit", "pos": (1.5, 7.5), "collected": False},
                {"type": "ammo", "pos": (9.5, 5.5), "collected": False},
                {"type": "ammo", "pos": (1.5, 11.5), "collected": False},
                {"type": "armor", "pos": (14.5, 9.5), "collected": False},
                {"type": "grenade", "pos": (7.5, 7.5), "collected": False},
                {"type": "stim", "pos": (10.5, 13.5), "collected": False},
            ]
            self.zombie_spawns = [
                {"type": "runner", "pos": (7.5, 3.5)},
                {"type": "walker", "pos": (11.5, 3.5)},
                {"type": "walker", "pos": (3.5, 5.5)},
                {"type": "runner", "pos": (13.5, 7.5)},
                {"type": "spitter", "pos": (5.5, 9.5)},
                {"type": "walker", "pos": (11.5, 9.5)},
                {"type": "runner", "pos": (4.5, 11.5)},
                {"type": "walker", "pos": (10.5, 11.5)},
                {"type": "spitter", "pos": (3.5, 14.5)},
            ]

        elif self.level_id == 3:
            # Level 3: City Center Barricade (Rescue: Military Scout)
            # Layout: Ruined Crossroads -> Police Outpost -> Checkpoint Charlie (Blue Keycard) -> APC Evac
            self.grid = [
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
                [w, _, _, _, w, _, _, _, _, _, _, _, _, _, _, w],
                [w, _, w, _, w, _, w, w, w, w, w, _, w, w, _, w],
                [w, _, w, _, _, _, _, _, _, _, w, _, _, w, _, w],
                [w, _, w, w, w, w, _, w, w, _, w, w, _, w, _, w],
                [w, _, _, _, _, w, _, w, _, _, _, w, _, _, _, w],
                [w, w, w, _, _, w, _, w, _, w, _, w, _, w, w, w],
                [w, _, _, _, _, _, _, _, _, w, _, _, _, _, _, w],
                [w, _, w, w, w, _, w, w, w, w, w, w, w, w, _, w],
                [w, _, w, _, _, _, _, _, _, _, _, _, _, w, _, w],
                [w, _, w, _, w, w, w, d, w, w, w, _, _, w, _, w],
                [w, _, _, _, w, _, _, _, _, _, w, _, _, _, _, w],
                [w, w, w, _, w, _, w, _, w, _, w, _, w, w, _, w],
                [w, _, _, _, _, _, w, _, w, _, _, _, _, w, _, w],
                [w, _, w, w, w, _, _, _, _, _, w, w, _, e, _, w],
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
            ]
            self.player_start = (2.5, 2.5)
            self.survivor_pos = (7.5, 12.5)
            self.extraction_pos = (13.5, 14.5)
            self.door_positions[(7, 10)] = {"locked": True, "required_keycard": "blue", "open": False}

            self.pickups = [
                {"type": "keycard_blue", "pos": (14.5, 1.5), "collected": False},
                {"type": "medkit", "pos": (1.5, 7.5), "collected": False},
                {"type": "medkit", "pos": (6.5, 13.5), "collected": False},
                {"type": "ammo", "pos": (7.5, 3.5), "collected": False},
                {"type": "ammo", "pos": (1.5, 11.5), "collected": False},
                {"type": "armor", "pos": (12.5, 7.5), "collected": False},
                {"type": "grenade", "pos": (14.5, 11.5), "collected": False},
                {"type": "stim", "pos": (3.5, 13.5), "collected": False},
            ]
            self.zombie_spawns = [
                {"type": "runner", "pos": (6.5, 1.5)},
                {"type": "walker", "pos": (12.5, 3.5)},
                {"type": "runner", "pos": (3.5, 5.5)},
                {"type": "spitter", "pos": (8.5, 5.5)},
                {"type": "walker", "pos": (5.5, 7.5)},
                {"type": "runner", "pos": (12.5, 7.5)},
                {"type": "brute", "pos": (7.5, 9.5)},  # Elite brute defender
                {"type": "walker", "pos": (2.5, 11.5)},
                {"type": "spitter", "pos": (12.5, 12.5)},
            ]

        elif self.level_id == 4:
            # Level 4: Industrial Chemical Plant (Rescue: Virology Specialist)
            # Layout: Toxic Slurry Pools -> Hazard Silos -> Decontamination Airlock (Green Keycard) -> Helipad
            self.grid = [
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
                [w, _, _, _, _, _, _, w, _, _, _, _, _, _, _, w],
                [w, _, w, w, w, w, _, w, _, w, w, w, w, w, _, w],
                [w, _, w, _, _, _, _, _, _, _, _, _, _, w, _, w],
                [w, _, w, _, w, w, w, w, w, w, w, w, _, w, _, w],
                [w, _, _, _, w, _, _, _, _, _, _, w, _, _, _, w],
                [w, w, w, _, w, _, w, w, w, w, _, w, _, w, w, w],
                [w, _, _, _, _, _, w, _, _, w, _, _, _, _, _, w],
                [w, _, w, w, w, _, w, _, _, w, _, w, w, w, _, w],
                [w, _, w, _, _, _, _, _, _, _, _, _, _, w, _, w],
                [w, _, w, _, w, w, w, d, w, w, w, w, _, w, _, w],
                [w, _, _, _, w, _, _, _, _, _, _, w, _, _, _, w],
                [w, w, w, _, w, _, w, _, w, w, _, w, _, w, w, w],
                [w, _, _, _, _, _, w, _, _, _, _, _, _, _, _, w],
                [w, _, w, w, w, w, w, _, w, w, w, w, w, e, _, w],
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
            ]
            self.player_start = (2.5, 2.5)
            self.survivor_pos = (8.5, 12.5)
            self.extraction_pos = (13.5, 14.5)
            self.door_positions[(7, 10)] = {"locked": True, "required_keycard": "green", "open": False}

            self.pickups = [
                {"type": "keycard_green", "pos": (14.5, 1.5), "collected": False},
                {"type": "medkit", "pos": (1.5, 5.5), "collected": False},
                {"type": "medkit", "pos": (7.5, 13.5), "collected": False},
                {"type": "ammo", "pos": (9.5, 3.5), "collected": False},
                {"type": "ammo", "pos": (14.5, 9.5), "collected": False},
                {"type": "armor", "pos": (1.5, 11.5), "collected": False},
                {"type": "grenade", "pos": (7.5, 7.5), "collected": False},
                {"type": "stim", "pos": (12.5, 13.5), "collected": False},
            ]
            self.zombie_spawns = [
                {"type": "spitter", "pos": (5.5, 1.5)},
                {"type": "spitter", "pos": (11.5, 3.5)},
                {"type": "runner", "pos": (3.5, 5.5)},
                {"type": "walker", "pos": (12.5, 5.5)},
                {"type": "spitter", "pos": (7.5, 7.5)},
                {"type": "runner", "pos": (3.5, 9.5)},
                {"type": "brute", "pos": (8.5, 9.5)},
                {"type": "runner", "pos": (13.5, 11.5)},
                {"type": "walker", "pos": (3.5, 13.5)},
                {"type": "spitter", "pos": (11.5, 13.5)},
            ]

        elif self.level_id == 5:
            # Level 5: Sub-level Research Lab (Rescue: Head Scientist)
            # Layout: Cryo Containment Vaults -> Bio-Core -> Hive Vault (Purple Master Card) -> Escape Lift
            self.grid = [
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
                [w, _, _, _, _, _, w, _, _, _, _, _, _, _, _, w],
                [w, _, w, w, w, _, w, _, w, w, w, w, w, w, _, w],
                [w, _, w, _, _, _, _, _, _, _, _, _, _, w, _, w],
                [w, _, w, _, w, w, w, w, w, w, w, w, _, w, _, w],
                [w, _, _, _, w, _, _, _, _, _, _, w, _, _, _, w],
                [w, w, w, _, w, _, w, w, w, w, _, w, w, w, _, w],
                [w, _, _, _, _, _, w, _, _, w, _, _, _, _, _, w],
                [w, _, w, w, w, _, w, _, _, w, _, w, w, w, _, w],
                [w, _, _, _, w, _, _, _, _, _, _, w, _, _, _, w],
                [w, w, w, _, w, w, w, d, w, w, w, w, _, w, w, w],
                [w, _, _, _, _, _, _, _, _, _, _, _, _, _, _, w],
                [w, _, w, w, w, w, w, _, w, w, w, w, w, w, _, w],
                [w, _, w, _, _, _, _, _, _, _, _, _, _, w, _, w],
                [w, _, _, _, w, _, _, _, _, w, _, _, _, e, _, w],
                [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
            ]
            self.player_start = (2.5, 2.5)
            self.survivor_pos = (7.5, 13.5)
            self.extraction_pos = (13.5, 14.5)
            self.door_positions[(7, 10)] = {"locked": True, "required_keycard": "purple", "open": False}

            self.pickups = [
                {"type": "keycard_purple", "pos": (14.5, 1.5), "collected": False},
                {"type": "medkit", "pos": (1.5, 7.5), "collected": False},
                {"type": "medkit", "pos": (9.5, 13.5), "collected": False},
                {"type": "ammo", "pos": (7.5, 3.5), "collected": False},
                {"type": "ammo", "pos": (14.5, 7.5), "collected": False},
                {"type": "armor", "pos": (1.5, 13.5), "collected": False},
                {"type": "grenade", "pos": (11.5, 9.5), "collected": False},
                {"type": "stim", "pos": (1.5, 3.5), "collected": False},
                {"type": "stim", "pos": (13.5, 13.5), "collected": False},
            ]
            self.zombie_spawns = [
                {"type": "runner", "pos": (5.5, 1.5)},
                {"type": "spitter", "pos": (11.5, 1.5)},
                {"type": "walker", "pos": (3.5, 3.5)},
                {"type": "brute", "pos": (9.5, 5.5)},   # Alpha brute
                {"type": "runner", "pos": (13.5, 5.5)},
                {"type": "spitter", "pos": (3.5, 7.5)},
                {"type": "walker", "pos": (12.5, 7.5)},
                {"type": "brute", "pos": (7.5, 8.5)},   # Hive Guardian boss
                {"type": "runner", "pos": (2.5, 11.5)},
                {"type": "spitter", "pos": (13.5, 11.5)},
            ]

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.parse_world_map()

    def parse_world_map(self):
        """Construct dictionary of solid tiles mapping (x, y) -> tile_id."""
        self.world_map = {}
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                if val:
                    self.world_map[(x, y)] = val

    def is_wall(self, x, y):
        """Check if grid coordinate contains a solid obstacle or locked door."""
        tile = (int(x), int(y))
        if tile in self.door_positions:
            # If door is open, it does not block
            return not self.door_positions[tile]["open"]
        return tile in self.world_map

    def get_tile_type(self, x, y):
        return self.world_map.get((int(x), int(y)), 0)

    def unlock_door(self, tile_pos):
        """Unlocks and opens security door."""
        if tile_pos in self.door_positions:
            self.door_positions[tile_pos]["open"] = True
            # Remove from collision map so player and entities can walk through
            if tile_pos in self.world_map:
                del self.world_map[tile_pos]
            return True
        return False
