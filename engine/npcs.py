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

        if self.norm_dist > 0.35 and abs(delta) < (math.pi / 2.2):
            delta_rays = delta / DELTA_ANGLE
            self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

            proj = (SCREEN_DIST / (self.norm_dist + 0.0001)) * self.scale
            proj_w = int(proj)
            proj_h = int(proj)

            if proj_w <= 0 or proj_h <= 0 or not self.current_surface:
                return None

            scaled_img = pg.transform.scale(self.current_surface, (proj_w, proj_h))

            # Apply distance shading
            if self.norm_dist > 3.0:
                dark_factor = min(0.65, (self.norm_dist - 3.0) / 18.0)
                dark_surf = pg.Surface((proj_w, proj_h)).convert_alpha()
                dark_surf.fill((0, 0, 0, int(dark_factor * 220)))
                scaled_img.blit(dark_surf, (0, 0))

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
    """Level specific VIP Survivor waiting for extraction."""
    def __init__(self, game, level_id, x, y):
        super().__init__(game, x, y, scale=0.78, height_shift=0.22)
        self.level_id = level_id
        self.frames = self.game.asset_manager.survivor_sprites.get(level_id, [])
        self.anim_idx = 0
        self.anim_timer = 0
        self.rescued = False
        self.current_surface = self.frames[0] if self.frames else None

    def update(self, dt):
        # Idle breathing / waving animation
        self.anim_timer += dt
        if self.anim_timer >= 450:
            self.anim_timer = 0
            self.anim_idx = (self.anim_idx + 1) % len(self.frames)
            self.current_surface = self.frames[self.anim_idx]

        # Check proximity to player
        dist = math.hypot(self.game.player.x - self.x, self.game.player.y - self.y)
        if dist < 2.0 and not self.rescued:
            self.game.player.near_survivor = self
        elif self.game.player.near_survivor == self and dist >= 2.0:
            self.game.player.near_survivor = None

    def rescue(self):
        if self.rescued:
            return
        self.rescued = True
        self.game.level_map.survivor_rescued = True
        self.game.level_map.extraction_unlocked = True
        self.game.sound_manager.play_rescue()
        self.game.hud.show_dialog_rescue(self.level_id)


class ZombieNPC(BaseSprite):
    """Aggressive zombie swarms: Walker, Runner, Spitter, and Brute."""
    def __init__(self, game, zombie_type, x, y):
        super().__init__(game, x, y, scale=0.75, height_shift=0.25)
        self.zombie_type = zombie_type
        self.alive = True
        self.state = "idle"  # idle, walk, attack, pain, death
        self.anim_idx = 0
        self.anim_timer = 0

        # Stats based on type
        if zombie_type == "runner":
            self.health = 70
            self.speed = 0.0028
            self.damage = 14
            self.attack_range = 1.1
            self.scale = 0.72
        elif zombie_type == "spitter":
            self.health = 80
            self.speed = 0.0018
            self.damage = 18
            self.attack_range = 3.5  # Ranged acid spitter
            self.scale = 0.80
        elif zombie_type == "brute":
            self.health = 260
            self.speed = 0.0015
            self.damage = 28
            self.attack_range = 1.3
            self.scale = 1.10
        else:  # walker
            self.health = 95
            self.speed = 0.0017
            self.damage = 12
            self.attack_range = 1.1
            self.scale = 0.78

        self.last_attack_time = 0
        self.attack_cooldown_ms = 900
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
