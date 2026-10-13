"""
NPCs & Interactive Sprites System:
Zombie Swarms, Level Survivor NPCs, World Pickups, and 2.5D Projection Pipeline.
"""
import math
import random
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, SCREEN_DIST,
    DELTA_ANGLE, HALF_NUM_RAYS, SCALE
)


class BaseSprite:
    """Base class for projected 2.5D sprite objects in raycast space."""
    def __init__(self, game, x, y, scale=0.75, height_shift=0.25):
        self.game = game
        self.x = x
        self.y = y
        self.scale = scale
        self.height_shift = height_shift
        self.dist = 0
        self.norm_dist = 0
        self.screen_x = 0
        self.current_surface = None

    def calculate_projection(self):
        player = self.game.player
        dx = self.x - player.x
        dy = self.y - player.y
        theta = math.atan2(dy, dx)

        delta = theta - player.angle
        while delta > math.pi:
            delta -= math.tau
        while delta < -math.pi:
            delta += math.tau

        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)

        if self.norm_dist > 0.08 and abs(delta) < (math.pi / 2.0):
            delta_rays = delta / DELTA_ANGLE
            self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

            proj = (SCREEN_DIST / (self.norm_dist + 0.0001)) * self.scale
            proj = min(HEIGHT * 3, proj)
            proj_w = max(1, int(proj))
            proj_h = max(1, int(proj))

            if not self.current_surface:
                return None

            scaled_img = pg.transform.scale(self.current_surface, (proj_w, proj_h))

            # Apply distance shading
            if self.norm_dist > 3.0:
                dark_factor = min(0.65, (self.norm_dist - 3.0) / 18.0)
                shade = int(255 * (1.0 - dark_factor))
                scaled_img.fill((shade, shade, shade), special_flags=pg.BLEND_MULT)

            pos_x = int(self.screen_x - proj_w // 2)
            pos_y = int(HALF_HEIGHT - proj_h // 2 + proj_h * self.height_shift)
            return (self.norm_dist, scaled_img, (pos_x, pos_y))
        return None


class PickupSprite(BaseSprite):
    """World item pickups: Medkits, Ammo, Armor, Keycards, Grenades, Stim."""
    def __init__(self, game, pickup_type, x, y):
        super().__init__(game, x, y, scale=0.45, height_shift=0.55)
        self.pickup_type = pickup_type
        self.collected = False
        self.current_surface = self.game.asset_manager.pickup_sprites.get(pickup_type)
        self.bob_phase = random.random() * math.tau

    def update(self, dt):
        if self.collected:
            return
        # Bobbing floating motion
        self.bob_phase += dt * 0.004
        self.height_shift = 0.50 + math.sin(self.bob_phase) * 0.06

        # Check collection distance to player
        dist = math.hypot(self.game.player.x - self.x, self.game.player.y - self.y)
        if dist < 0.75:
            self.collect()

    def collect(self):
        self.collected = True
        self.game.sound_manager.play_pickup()
        inv = self.game.weapon_manager.inventory

        if self.pickup_type == "medkit":
            inv["medkit"] = min(5, inv["medkit"] + 1)
            self.game.hud.show_message("+1 Trauma Medkit Collected!", (40, 220, 80))
        elif self.pickup_type == "ammo":
            # Add ammo to all weapons
            for w in self.game.weapon_manager.ammo_state:
                self.game.weapon_manager.ammo_state[w][1] += 24
            self.game.hud.show_message("+24 Ammo Box Loaded!", (240, 200, 30))
        elif self.pickup_type == "armor":
            self.game.player.armor = 100
            self.game.hud.show_message("+100 Armor Vest Equipped!", (40, 180, 240))
        elif self.pickup_type == "grenade":
            inv["grenade"] = min(5, inv["grenade"] + 1)
            self.game.hud.show_message("+1 M67 Frag Grenade Collected!", (220, 120, 40))
        elif self.pickup_type == "stim":
            inv["stim"] = min(3, inv["stim"] + 1)
            self.game.hud.show_message("+1 Adrenaline Stim Acquired!", (0, 230, 255))
        elif self.pickup_type.startswith("keycard_"):
            kc_color = self.pickup_type.split("_")[1]
            inv["keycards"].add(kc_color)
            self.game.hud.show_message(f"SECURITY KEYCARD ACQUIRED ({kc_color.upper()})!", (255, 230, 40))


class SurvivorNPC(BaseSprite):
    """Level specific VIP Survivor waiting for extraction with audio/visual help shouts and escort behavior."""
    def __init__(self, game, level_id, x, y):
        super().__init__(game, x, y, scale=0.78, height_shift=0.22)
        self.level_id = level_id
        self.frames = self.game.asset_manager.survivor_sprites.get(level_id, [])
        self.anim_idx = 0
        self.anim_timer = 0
        self.rescued = False
        self.current_surface = self.frames[0] if self.frames else None
        self.shout_cooldown = 1200
        self.shouts = [
            "HELP! OVER HERE, SERGEANT!",
            "PLEASE SAVE ME! I'M TRAPPED IN HERE!",
            "SERGEANT VANCE! BEHIND THIS DOOR!",
            "HELP ME! THE HORDE IS CLOSING IN!",
            "OVER HERE! I HAVE THE RESEARCH INTEL!",
        ]

    def update(self, dt):
        # Idle breathing / waving animation
        self.anim_timer += dt
        if self.anim_timer >= 450:
            self.anim_timer = 0
            self.anim_idx = (self.anim_idx + 1) % len(self.frames) if self.frames else 0
            if self.frames:
                self.current_surface = self.frames[self.anim_idx]

        dist = math.hypot(self.game.player.x - self.x, self.game.player.y - self.y)

        # 1. Proximity Shouting for Help (when player gets closer and survivor is still trapped)
        if not self.rescued:
            if dist <= 6.5:
                self.shout_cooldown -= dt
                if self.shout_cooldown <= 0:
                    self.shout_cooldown = 3500
                    shout_msg = random.choice(self.shouts)
                    meta = self.game.level_map.meta
                    self.game.hud.show_message(f"🚨 {meta['survivor'].upper()}: \"{shout_msg}\"", (255, 215, 50), 3200)
                    if hasattr(self.game.sound_manager, "play_survivor_help"):
                        self.game.sound_manager.play_survivor_help()
                    else:
                        self.game.sound_manager.play("rescue")

            # Check interaction range for keycard unlock/rescue
            if dist < 2.0:
                self.game.player.near_survivor = self
            elif self.game.player.near_survivor == self and dist >= 2.0:
                self.game.player.near_survivor = None

        # 2. Rescued Companion Escort Follower: follows behind player toward EVAC
        else:
            if dist > 1.6:
                angle = math.atan2(self.game.player.y - self.y, self.game.player.x - self.x)
                speed = 0.0022 * dt
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                if not self.game.level_map.is_wall(self.x + dx * 1.5, self.y):
                    self.x += dx
                if not self.game.level_map.is_wall(self.x, self.y + dy * 1.5):
                    self.y += dy

    def rescue(self):
        if self.rescued:
            return
        self.rescued = True
        self.game.level_map.survivor_rescued = True
        self.game.level_map.extraction_unlocked = True
        self.game.sound_manager.play_rescue()
        meta = self.game.level_map.meta
        self.game.hud.show_message(
            f"★ RESCUED {meta['survivor'].upper()}! \"Thank you Vance, I'm right behind you to Evac!\"",
            (60, 240, 120), 4500
        )


class ZombieNPC(BaseSprite):
    """Aggressive zombie swarms with Level-by-Level difficulty progression."""
    def __init__(self, game, zombie_type, x, y):
        super().__init__(game, x, y, scale=0.75, height_shift=0.25)
        self.zombie_type = zombie_type
        self.alive = True
        self.state = "idle"  # idle, walk, attack, pain, death
        self.anim_idx = 0
        self.anim_timer = 0

        # Level-by-Level Difficulty Scaling (Level 1 = normal, Level 8 = lethal hazard)
        lvl = getattr(self.game.level_map, "level_id", 1)
        diff_hp = 1.0 + (lvl - 1) * 0.18    # +18% HP per level tier
        diff_dmg = 1.0 + (lvl - 1) * 0.14   # +14% damage per level tier
        diff_spd = 1.0 + (lvl - 1) * 0.05   # +5% speed per level tier

        # Stats calibrated with difficulty multipliers
        if zombie_type == "runner":
            self.health = int(70 * diff_hp)
            self.speed = 0.0028 * diff_spd
            self.damage = int(14 * diff_dmg)
            self.attack_range = 1.1
            self.scale = 0.60
            self.height_shift = 0.38
        elif zombie_type == "spitter":
            self.health = int(80 * diff_hp)
            self.speed = 0.0018 * diff_spd
            self.damage = int(18 * diff_dmg)
            self.attack_range = 3.5  # Ranged acid spitter
            self.scale = 0.70
            self.height_shift = 0.27
        elif zombie_type == "brute":
            self.health = int(260 * diff_hp)
            self.speed = 0.0015 * diff_spd
            self.damage = int(28 * diff_dmg)
            self.attack_range = 1.3
            self.scale = 1.00
            self.height_shift = 0.04
        else:  # walker
            self.health = int(95 * diff_hp)
            self.speed = 0.0017 * diff_spd
            self.damage = int(12 * diff_dmg)
            self.attack_range = 1.1
            self.scale = 0.60
            self.height_shift = 0.38

        self.last_attack_time = 0
        self.attack_cooldown_ms = max(550, int(900 - (lvl - 1) * 45))
        self.current_surface = self.get_frame("idle", 0)

    def get_frame(self, state, idx):
        frames = self.game.asset_manager.zombie_sprites.get(self.zombie_type, {}).get(state, [])
        if frames:
            return frames[idx % len(frames)]
        return None

    def take_damage(self, dmg):
        if not self.alive:
            return
        self.health -= dmg
        self.game.sound_manager.play_zombie_pain()
        if self.health <= 0:
            self.die()
        else:
            self.state = "pain"
            self.anim_timer = 0
            self.current_surface = self.get_frame("walk", 0)

    def die(self):
        self.alive = False
        self.state = "death"
        self.anim_idx = 0
        self.anim_timer = 0
        self.game.sound_manager.play_zombie_death()
        self.game.player.kills += 1

        # Chance to drop ammo or medkit
        drop_roll = random.random()
        if drop_roll < 0.25:
            self.game.sprite_manager.spawn_pickup("ammo", self.x, self.y)
        elif drop_roll < 0.40:
            self.game.sprite_manager.spawn_pickup("medkit", self.x, self.y)

    def update_ai(self, dt):
        if not self.alive:
            return

        now = pg.time.get_ticks()
        px, py = self.game.player.x, self.game.player.y
        dist_to_player = math.hypot(px - self.x, py - self.y)

        # Line of sight check
        has_los = not self.game.weapon_manager.check_wall_between(self.x, self.y, px, py)

        # Attack logic
        if dist_to_player <= self.attack_range and has_los:
            self.state = "attack"
            if now - self.last_attack_time >= self.attack_cooldown_ms:
                self.last_attack_time = now
                self.game.sound_manager.play_zombie_attack()
                self.game.player.take_damage(self.damage)
            return

        # Pursuit logic
        if has_los or dist_to_player < 8.0:
            self.state = "walk"
            # Steer towards player using pathfinding step or direct vector
            if has_los:
                angle = math.atan2(py - self.y, px - self.x)
                dx = math.cos(angle) * self.speed * dt
                dy = math.sin(angle) * self.speed * dt
            else:
                next_tile = self.game.pathfinding.get_next_step(
                    (int(self.x), int(self.y)), (int(px), int(py))
                )
                tx = next_tile[0] + 0.5
                ty = next_tile[1] + 0.5
                angle = math.atan2(ty - self.y, tx - self.x)
                dx = math.cos(angle) * self.speed * dt
                dy = math.sin(angle) * self.speed * dt

            # Wall collision checking
            if not self.game.level_map.is_wall(self.x + dx * 1.5, self.y):
                self.x += dx
            if not self.game.level_map.is_wall(self.x, self.y + dy * 1.5):
                self.y += dy

    def update(self, dt):
        self.update_ai(dt)

        # Update animation frames
        self.anim_timer += dt
        frame_time = 140 if self.state == "walk" else 200

        if self.state == "death":
            death_frames = self.game.asset_manager.zombie_sprites.get(self.zombie_type, {}).get("death", [])
            if self.anim_timer >= 180 and self.anim_idx < len(death_frames) - 1:
                self.anim_timer = 0
                self.anim_idx += 1
            self.current_surface = self.get_frame("death", self.anim_idx)
        else:
            if self.anim_timer >= frame_time:
                self.anim_timer = 0
                self.anim_idx += 1
            self.current_surface = self.get_frame(self.state, self.anim_idx)


class SpriteManager:
    """Orchestrates all active entities, pickups, survivors, and projected render surfaces."""
    def __init__(self, game):
        self.game = game
        self.zombies = []
        self.pickups = []
        self.survivor = None
        self.sprites_to_render = []
        self.load_level_entities()

    def load_level_entities(self):
        self.zombies.clear()
        self.pickups.clear()

        # Load pickups from level map
        for p in self.game.level_map.pickups:
            if not p["collected"]:
                self.pickups.append(PickupSprite(self.game, p["type"], p["pos"][0], p["pos"][1]))

        # Load Survivor
        spos = self.game.level_map.survivor_pos
        self.survivor = SurvivorNPC(self.game, self.game.level_map.level_id, spos[0], spos[1])

        # Load Zombies
        for z in self.game.level_map.zombie_spawns:
            self.zombies.append(ZombieNPC(self.game, z["type"], z["pos"][0], z["pos"][1]))

    def spawn_pickup(self, ptype, x, y):
        self.pickups.append(PickupSprite(self.game, ptype, x, y))

    def update(self, dt):
        self.sprites_to_render = []

        # Update pickups
        for p in self.pickups:
            if not p.collected:
                p.update(dt)
                proj = p.calculate_projection()
                if proj:
                    self.sprites_to_render.append(proj)

        # Update survivor
        if self.survivor:
            self.survivor.update(dt)
            proj = self.survivor.calculate_projection()
            if proj:
                self.sprites_to_render.append(proj)

        # Update zombies
        for z in self.zombies:
            z.update(dt)
            proj = z.calculate_projection()
            if proj:
                self.sprites_to_render.append(proj)
