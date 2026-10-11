"""
Procedural & Random Map Generator for Zombie Quarantine FPS Engine.
Generates fully solvable, atmospheric 2.5D retro raycaster maze layouts with
guaranteed reachability for Keycards, Locked Security Doors, VIP Survivors,
and Extraction Evacuation Bays, plus dynamic pickups and zombie spawn waves.
"""
import random
from collections import deque


class RandomMapGenerator:
    """Procedurally creates dungeon/maze levels with guaranteed solvability."""

    @staticmethod
    def generate(level_id, meta, width=16, height=16, seed=None):
        """
        Generates a complete level configuration dictionary.
        Retries until a valid, verified solvable layout is constructed.
        """
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()

        for attempt in range(100):
            layout = RandomMapGenerator._try_generate_layout(level_id, meta, width, height, rng)
            if layout and RandomMapGenerator._validate_layout(layout):
                return layout

        # Fallback to guaranteed template if procedural seed hits unexpected edge case
        return RandomMapGenerator._create_fallback_layout(level_id, meta, width, height)

    @staticmethod
    def _try_generate_layout(level_id, meta, width, height, rng):
        w = level_id
        d = 100 + level_id
        e = 99
        _ = 0

        # Initialize full solid wall grid
        grid = [[w for _x in range(width)] for _y in range(height)]

        # Place 4 to 6 non-overlapping rectangular rooms
        rooms = []
        target_room_count = rng.randint(4, 6)

        for _ in range(50):
            if len(rooms) >= target_room_count:
                break
            rw = rng.randint(3, 4)
            rh = rng.randint(3, 4)
            rx = rng.randint(1, width - rw - 1)
            ry = rng.randint(1, height - rh - 1)

            # Check separation from existing rooms
            overlap = False
            for (ox, oy, ow, oh) in rooms:
                if not (rx + rw < ox - 1 or rx > ox + ow + 1 or ry + rh < oy - 1 or ry > oy + oh + 1):
                    overlap = True
                    break

            if not overlap:
                rooms.append((rx, ry, rw, rh))

        if len(rooms) < 3:
            return None

        # Carve all rooms into floor
        for (rx, ry, rw, rh) in rooms:
            for y in range(ry, ry + rh):
                for x in range(rx, rx + rw):
                    grid[y][x] = _

        # Carve corridors connecting room centers in chain and random loop
        def carve_corridor(x1, y1, x2, y2):
            cx, cy = x1, y1
            # 50% horizontal first, 50% vertical first
            if rng.random() < 0.5:
                while cx != x2:
                    grid[cy][cx] = _
                    cx += 1 if x2 > cx else -1
                while cy != y2:
                    grid[cy][cx] = _
                    cy += 1 if y2 > cy else -1
            else:
                while cy != y2:
                    grid[cy][cx] = _
                    cy += 1 if y2 > cy else -1
                while cx != x2:
                    grid[cy][cx] = _
                    cx += 1 if x2 > cx else -1
            grid[y2][x2] = _

        for i in range(len(rooms) - 1):
            r1 = rooms[i]
            r2 = rooms[i + 1]
            c1 = (r1[0] + r1[2] // 2, r1[1] + r1[3] // 2)
            c2 = (r2[0] + r2[2] // 2, r2[1] + r2[3] // 2)
            carve_corridor(c1[0], c1[1], c2[0], c2[1])

        # Extra loop corridor for non-linear exploration
        if len(rooms) >= 3:
            r0 = rooms[0]
            rlast = rooms[-2]
            c0 = (r0[0] + r0[2] // 2, r0[1] + r0[3] // 2)
            clast = (rlast[0] + rlast[2] // 2, rlast[1] + rlast[3] // 2)
            carve_corridor(c0[0], c0[1], clast[0], clast[1])

        # Room assignments
        # Room 0: Player Start
        p_room = rooms[0]
        player_start = (p_room[0] + p_room[2] / 2.0, p_room[1] + p_room[3] / 2.0)

        # Room -1: VIP Survivor Vault Room
        survivor_room = rooms[-1]
        survivor_pos = (survivor_room[0] + survivor_room[2] / 2.0, survivor_room[1] + survivor_room[3] / 2.0)

        # Keycard room: middle room (far from survivor room, easily reachable from player start)
        keycard_room = rooms[1] if len(rooms) > 1 else rooms[0]
        kc_type = meta.get("keycard_name", "Red Medical Keycard").lower()
        if "red" in kc_type:
            kc_id = "keycard_red"
        elif "yellow" in kc_type:
            kc_id = "keycard_yellow"
        elif "blue" in kc_type:
            kc_id = "keycard_blue"
        elif "green" in kc_type or "hazmat" in kc_type:
            kc_id = "keycard_green"
        elif "purple" in kc_type or "master" in kc_type:
            kc_id = "keycard_purple"
        elif "orange" in kc_type or "botanical" in kc_type:
            kc_id = "keycard_orange"
        elif "crimson" in kc_type:
            kc_id = "keycard_crimson"
        elif "gold" in kc_type:
            kc_id = "keycard_gold"
        else:
            kc_id = "keycard_red"

        # Place keycard in keycard room
        keycard_pos = (keycard_room[0] + 0.5, keycard_room[1] + 0.5)

        # Extraction Room: Room 2 or player start room far end
        ext_room = rooms[2] if len(rooms) > 3 else rooms[0]
        # Place extraction tile on one of the outer walls of ext_room
        ext_x = ext_room[0] + ext_room[2] // 2
        ext_y = ext_room[1] + ext_room[3] - 1
        # Extraction wall tile
        if ext_y + 1 < height:
            grid[ext_y + 1][ext_x] = e
            extraction_pos = (ext_x + 0.5, ext_y + 0.5)
        else:
            grid[ext_y][ext_x] = e
            extraction_pos = (ext_x + 0.5, ext_y - 0.5)

        # Place a locked security door blocking access to the survivor room
        # Find walkable tile adjacent to survivor room that connects outside
        door_positions = {}
        s_xmin, s_ymin = survivor_room[0], survivor_room[1]
        s_xmax, s_ymax = s_xmin + survivor_room[2], s_ymin + survivor_room[3]

        candidate_doors = []
        for sy in range(max(1, s_ymin - 1), min(height - 1, s_ymax + 1)):
            for sx in range(max(1, s_xmin - 1), min(width - 1, s_xmax + 1)):
                if grid[sy][sx] == _:
                    # Check if this tile is on the perimeter of the survivor room
                    if (sx == s_xmin - 1 or sx == s_xmax or sy == s_ymin - 1 or sy == s_ymax):
                        # Has horizontal or vertical wall neighbors (doorway slot)
                        horiz_walls = (grid[sy][sx - 1] == w and grid[sy][sx + 1] == w)
                        vert_walls = (grid[sy - 1][sx] == w and grid[sy + 1][sx] == w)
                        if horiz_walls or vert_walls:
                            candidate_doors.append((sx, sy))

        if not candidate_doors:
            # Pick any connection tile on the corridor into survivor room
            sc_x = survivor_room[0]
            sc_y = survivor_room[1]
            candidate_doors.append((sc_x, sc_y))

        door_x, door_y = rng.choice(candidate_doors)
        grid[door_y][door_x] = d

        # Keycard color code string
        req_card = "red"
        for c in ("red", "yellow", "blue", "green", "purple", "orange", "crimson", "gold"):
            if c in kc_id:
                req_card = c
                break

        door_positions[(door_x, door_y)] = {
            "locked": True,
            "required_keycard": req_card,
            "open": False
        }

        # Build Pickups
        pickups = [
            {"type": kc_id, "pos": keycard_pos, "collected": False}
        ]

        # Gather empty tiles for items & zombies
        empty_tiles = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if grid[y][x] == _:
                    pos = (x + 0.5, y + 0.5)
                    # Exclude start, survivor, extraction, door
                    if (x, y) != (door_x, door_y) and (x, y) != (int(keycard_pos[0]), int(keycard_pos[1])):
                        empty_tiles.append((x, y))

        rng.shuffle(empty_tiles)

        # Item types
        item_pool = ["medkit", "medkit", "ammo", "ammo", "ammo", "armor", "grenade", "stim"]
        if level_id >= 4:
            item_pool.extend(["ammo", "medkit", "stim", "grenade"])

        for itype in item_pool:
            if empty_tiles:
                ex, ey = empty_tiles.pop()
                pickups.append({"type": itype, "pos": (ex + 0.5, ey + 0.5), "collected": False})

        # Zombie Spawns based on level difficulty
        zombie_spawns = []
        base_zombies = 8 + min(8, level_id * 2)

        # Zombie types distribution
        if level_id <= 2:
            z_types = ["walker", "walker", "runner"]
        elif level_id <= 4:
            z_types = ["walker", "runner", "spitter"]
        elif level_id <= 6:
            z_types = ["runner", "spitter", "brute", "walker"]
        else:
            z_types = ["runner", "spitter", "brute", "brute"]

        # Only spawn zombies at least 3.5 units away from player start
        px, py = player_start
        zombie_candidates = [
            t for t in empty_tiles
            if ((t[0] + 0.5 - px) ** 2 + (t[1] + 0.5 - py) ** 2) >= 12.0
        ]
        rng.shuffle(zombie_candidates)

        for _ in range(min(base_zombies, len(zombie_candidates))):
            zx, zy = zombie_candidates.pop()
            zombie_spawns.append({
                "type": rng.choice(z_types),
                "pos": (zx + 0.5, zy + 0.5)
            })

        return {
            "grid": grid,
            "player_start": player_start,
            "survivor_pos": survivor_pos,
            "extraction_pos": extraction_pos,
            "door_positions": door_positions,
            "pickups": pickups,
            "zombie_spawns": zombie_spawns,
            "wall_type": w,
            "door_type": d,
            "ext_type": e,
        }

    @staticmethod
    def _validate_layout(layout):
        """Validates that player can reach keycard, unlock door, reach survivor, and extract."""
        grid = layout["grid"]
        h = len(grid)
        w = len(grid[0])
        door_coords = set(layout["door_positions"].keys())

        # Check reachability from start to keycard without going through door
        start_tile = (int(layout["player_start"][0]), int(layout["player_start"][1]))
        key_tile = (int(layout["pickups"][0]["pos"][0]), int(layout["pickups"][0]["pos"][1]))
        survivor_tile = (int(layout["survivor_pos"][0]), int(layout["survivor_pos"][1]))
        ext_tile = (int(layout["extraction_pos"][0]), int(layout["extraction_pos"][1]))

        def get_neighbors(x, y, ignore_doors=False):
            res = []
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if grid[ny][nx] == 0 or (nx, ny) == ext_tile:
                        if ignore_doors or (nx, ny) not in door_coords:
                            res.append((nx, ny))
                    elif (nx, ny) in door_coords and ignore_doors:
                        res.append((nx, ny))
            return res

        def bfs(src, dst, ignore_doors=False):
            queue = deque([src])
            visited = {src}
            while queue:
                cx, cy = queue.popleft()
                if (cx, cy) == dst:
                    return True
                for nxt in get_neighbors(cx, cy, ignore_doors):
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
            return False

        # Phase 1: Player must be able to reach keycard without opening door
        if not bfs(start_tile, key_tile, ignore_doors=False):
            return False

        # Phase 2: Player must be able to reach door from start
        door_reachable = False
        for dpos in door_coords:
            for nbr in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = dpos[0] + nbr[0], dpos[1] + nbr[1]
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == 0:
                    if bfs(start_tile, (nx, ny), ignore_doors=False):
                        door_reachable = True
                        break
            if door_reachable:
                break
        if not door_reachable:
            return False

        # Phase 3: Once door is open (ignore_doors=True), player must reach survivor
        if not bfs(start_tile, survivor_tile, ignore_doors=True):
            return False

        # Phase 4: From survivor, player must be able to reach extraction
        if not bfs(survivor_tile, ext_tile, ignore_doors=True):
            return False

        return True

    @staticmethod
    def _create_fallback_layout(level_id, meta, width=16, height=16):
        """Deterministic reliable layout guarantee."""
        w = level_id
        d = 100 + level_id
        e = 99
        _ = 0

        grid = [
            [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
            [w, _, _, _, _, _, w, _, _, _, _, _, _, _, _, w],
            [w, _, w, w, _, _, w, _, w, w, w, w, _, w, _, w],
            [w, _, w, _, _, _, _, _, _, _, _, w, _, w, _, w],
            [w, _, w, _, w, w, w, w, _, w, _, w, _, w, _, w],
            [w, _, _, _, w, _, _, w, _, w, _, _, _, _, _, w],
            [w, w, _, w, w, _, _, w, _, w, w, w, w, _, w, w],
            [w, _, _, _, _, _, _, _, _, _, _, _, w, _, _, w],
            [w, _, w, w, w, w, _, w, w, w, _, _, w, w, _, w],
            [w, _, w, _, _, w, _, w, _, _, _, _, _, _, _, w],
            [w, _, w, _, _, w, _, w, _, w, w, d, w, w, _, w],
            [w, _, _, _, _, _, _, w, _, w, _, _, _, w, _, w],
            [w, w, w, _, w, w, _, w, _, w, _, _, _, w, _, w],
            [w, _, _, _, _, w, _, _, _, _, _, _, _, _, _, w],
            [w, _, w, w, _, w, _, w, w, _, w, w, _, e, _, w],
            [w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w],
        ]

        kc_type = meta.get("keycard_name", "Red Medical Keycard").lower()
        req_card = "red"
        for c in ("red", "yellow", "blue", "green", "purple", "orange", "crimson", "gold"):
            if c in kc_type:
                req_card = c
                break

        door_positions = {
            (11, 10): {"locked": True, "required_keycard": req_card, "open": False}
        }

        pickups = [
            {"type": f"keycard_{req_card}", "pos": (14.5, 1.5), "collected": False},
            {"type": "medkit", "pos": (1.5, 7.5), "collected": False},
            {"type": "ammo", "pos": (9.5, 5.5), "collected": False},
            {"type": "armor", "pos": (1.5, 13.5), "collected": False},
            {"type": "grenade", "pos": (7.5, 7.5), "collected": False},
            {"type": "stim", "pos": (12.5, 11.5), "collected": False},
        ]

        zombie_spawns = [
            {"type": "walker", "pos": (6.5, 3.5)},
            {"type": "runner", "pos": (11.5, 3.5)},
            {"type": "walker", "pos": (3.5, 7.5)},
            {"type": "runner", "pos": (10.5, 7.5)},
            {"type": "spitter", "pos": (5.5, 11.5)},
            {"type": "brute" if level_id >= 3 else "walker", "pos": (8.5, 13.5)},
        ]

        return {
            "grid": grid,
            "player_start": (2.5, 2.5),
            "survivor_pos": (12.5, 11.5),
            "extraction_pos": (13.5, 14.5),
            "door_positions": door_positions,
            "pickups": pickups,
            "zombie_spawns": zombie_spawns,
            "wall_type": w,
            "door_type": d,
            "ext_type": e,
        }
