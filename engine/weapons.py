"""
Weapons & Tactical Equipment System.
Supports Pistol, Combat Shotgun, Assault Rifle, Frag Grenades, Medkits, Armor, and Adrenaline.
"""
import math
import random
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, WEAPON_CONFIGS, TACTICAL_CONFIGS
)


class Grenade:
    """Thrown explosive entity with timer and AoE detonation."""
    def __init__(self, game, x, y, angle):
        self.game = game
        self.x = x
        self.y = y
        speed = 0.007
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.fuse_time = TACTICAL_CONFIGS["grenade"]["fuse_time_ms"]
        self.timer = 0
        self.exploded = False
        self.radius = TACTICAL_CONFIGS["grenade"]["radius"]
        self.damage = TACTICAL_CONFIGS["grenade"]["damage"]

    def update(self, dt):
        if self.exploded:
            return
        self.timer += dt
        # Move grenade until wall collision
        next_x = self.x + self.vx * dt
        next_y = self.y + self.vy * dt
        if not self.game.level_map.is_wall(next_x, self.y):
            self.x = next_x
        else:
            self.vx *= -0.5  # Bounce
        if not self.game.level_map.is_wall(self.x, next_y):
            self.y = next_y
        else:
            self.vy *= -0.5

        # Friction
        self.vx *= 0.96
        self.vy *= 0.96

        if self.timer >= self.fuse_time:
            self.detonate()

    def detonate(self):
        self.exploded = True
        self.game.sound_manager.play_grenade()
        self.game.object_renderer.trigger_flash(220)

        # AoE damage to all zombies within radius
        for npc in self.game.sprite_manager.zombies:
            if not npc.alive:
                continue
            dist = math.hypot(npc.x - self.x, npc.y - self.y)
            if dist <= self.radius:
                # Falloff damage
                falloff = (1.0 - (dist / self.radius))
                dmg = int(self.damage * falloff)
                npc.take_damage(dmg)


class WeaponManager:
    """Manages active weapons, ammunition, reload sequences, and first-person viewmodels."""

    def __init__(self, game):
        self.game = game
        self.available_weapons = ["pistol", "shotgun", "rifle"]
        self.current_weapon_idx = 0
        self.current_weapon_key = "pistol"

        # Ammo state per weapon: [in_clip, reserve]
        self.ammo_state = {
            "pistol": [
                WEAPON_CONFIGS["pistol"]["max_ammo"],
                WEAPON_CONFIGS["pistol"]["reserve_ammo"]
            ],
            "shotgun": [
                WEAPON_CONFIGS["shotgun"]["max_ammo"],
                WEAPON_CONFIGS["shotgun"]["reserve_ammo"]
            ],
            "rifle": [
                WEAPON_CONFIGS["rifle"]["max_ammo"],
                WEAPON_CONFIGS["rifle"]["reserve_ammo"]
            ],
        }

        # Tactical equipment inventory
        self.inventory = {
            "medkit": 2,
            "grenade": 2,
            "armor": 100,  # 100 armor vest points
            "stim": 1,
            "keycards": set()  # set of keycard names, e.g. {"red"}
        }

        # Firing and reloading state
        self.is_firing = False
        self.is_reloading = False
        self.last_shot_time = 0
        self.reload_start_time = 0
        self.anim_frame = 0
        self.anim_timer = 0

        # Active grenades in the level
        self.active_grenades = []

    @property
    def current_config(self):
        return WEAPON_CONFIGS[self.current_weapon_key]

    def switch_weapon(self, direction=1):
        """Cycle to next or previous weapon."""
        if self.is_reloading:
            return
        self.current_weapon_idx = (self.current_weapon_idx + direction) % len(self.available_weapons)
        self.current_weapon_key = self.available_weapons[self.current_weapon_idx]
        self.is_firing = False
        self.anim_frame = 0
        self.game.sound_manager.play_reload()

    def select_weapon(self, weapon_name):
        if weapon_name in self.available_weapons:
            self.current_weapon_idx = self.available_weapons.index(weapon_name)
            self.current_weapon_key = weapon_name
            self.is_firing = False
            self.is_reloading = False
            self.anim_frame = 0

    def start_reload(self):
        clip, reserve = self.ammo_state[self.current_weapon_key]
        max_clip = self.current_config["max_ammo"]
        if self.is_reloading or clip >= max_clip or reserve <= 0:
            return
        self.is_reloading = True
        self.reload_start_time = pg.time.get_ticks()
        self.game.sound_manager.play_reload()

    def update_reload(self, now):
        if not self.is_reloading:
            return
        reload_dur = self.current_config["reload_time_ms"]
        if now - self.reload_start_time >= reload_dur:
            clip, reserve = self.ammo_state[self.current_weapon_key]
            needed = self.current_config["max_ammo"] - clip
            to_add = min(needed, reserve)
            self.ammo_state[self.current_weapon_key][0] += to_add
            self.ammo_state[self.current_weapon_key][1] -= to_add
            self.is_reloading = False

    def shoot(self):
        now = pg.time.get_ticks()
        cfg = self.current_config
        if self.is_reloading or (now - self.last_shot_time < cfg["fire_rate_ms"]):
            return False

        clip, reserve = self.ammo_state[self.current_weapon_key]
        if clip <= 0:
            self.game.sound_manager.play_reload()
            self.start_reload()
            return False

        # Deduct ammo
        self.ammo_state[self.current_weapon_key][0] -= 1
        self.last_shot_time = now
        self.is_firing = True
        self.anim_frame = 1  # Muzzle flash frame
        self.anim_timer = 90  # Duration of flash frame in ms
        self.game.player.shots_fired += 1

        # Play weapon audio
        if self.current_weapon_key == "pistol":
            self.game.sound_manager.play_pistol()
        elif self.current_weapon_key == "shotgun":
            self.game.sound_manager.play_shotgun()
        elif self.current_weapon_key == "rifle":
            self.game.sound_manager.play_rifle()

        # Trigger object renderer muzzle flash
        self.game.object_renderer.trigger_flash(100)

        # Raycast Hitscan weapon trace
        pellets = cfg["pellets"]
        spread = cfg["spread"]
        dmg = cfg["damage"]

        for _ in range(pellets):
            pellet_angle = self.game.player.angle + (random.random() * 2 - 1) * spread
            self.perform_hitscan(pellet_angle, dmg)

        # Auto reload if empty
        if self.ammo_state[self.current_weapon_key][0] == 0:
            self.start_reload()

        return True

    def perform_hitscan(self, angle, damage):
        """Raycast hitscan check against all active zombies in player's field of fire."""
        hit_npc = None
        min_dist = float('inf')

        # Check all alive zombies
        for npc in self.game.sprite_manager.zombies:
            if not npc.alive:
                continue
            # Calculate angle to zombie
            dx = npc.x - self.game.player.x
            dy = npc.y - self.game.player.y
            theta = math.atan2(dy, dx)
            delta = theta - angle
            # Normalize angle difference
            while delta > math.pi:
                delta -= math.tau
            while delta < -math.pi:
                delta += math.tau

            # Check if zombie is in front of the ray within angular tolerance
            dist = math.hypot(dx, dy)
            angular_width = math.atan2(0.45, dist)  # Hitbox radius ~0.45 units
            if abs(delta) < angular_width:
                # Check for blocking wall between player and zombie
                if not self.check_wall_between(self.game.player.x, self.game.player.y, npc.x, npc.y):
                    if dist < min_dist:
                        min_dist = dist
                        hit_npc = npc

        if hit_npc:
            self.game.player.shots_hit += 1
            hit_npc.take_damage(damage)

    def check_wall_between(self, x1, y1, x2, y2):
        """Step along ray to check if wall obstructs line of sight."""
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = max(2, int(dist * 6))
        for i in range(1, steps):
            t = i / steps
            cx = x1 + (x2 - x1) * t
            cy = y1 + (y2 - y1) * t
            if self.game.level_map.is_wall(cx, cy):
                return True
        return False

    def throw_grenade(self):
        if self.inventory["grenade"] <= 0:
            return False
        self.inventory["grenade"] -= 1
        g = Grenade(self.game, self.game.player.x, self.game.player.y, self.game.player.angle)
        self.active_grenades.append(g)
        return True

    def use_medkit(self):
        if self.inventory["medkit"] <= 0 or self.game.player.health >= 100:
            return False
        self.inventory["medkit"] -= 1
        heal = TACTICAL_CONFIGS["medkit"]["heal_amount"]
        self.game.player.health = min(100, self.game.player.health + heal)
        self.game.sound_manager.play_pickup()
        return True

    def use_adrenaline(self):
        if self.inventory["stim"] <= 0:
            return False
        self.inventory["stim"] -= 1
        self.game.player.apply_adrenaline()
        self.game.sound_manager.play_adrenaline()
        return True

    def update(self, dt):
        now = pg.time.get_ticks()
        self.update_reload(now)

        # Update firing viewmodel animation frame
        if self.is_firing:
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                self.is_firing = False
                self.anim_frame = 0

        # Update active grenades
        for g in list(self.active_grenades):
            g.update(dt)
            if g.exploded:
                self.active_grenades.remove(g)

    def draw_viewmodel(self, screen):
        """Draws first-person weapon viewmodel centered at the bottom of the screen."""
        frames = self.game.asset_manager.weapon_sprites.get(self.current_weapon_key, [])
        if not frames:
            return

        frame_idx = min(self.anim_frame, len(frames) - 1)
        frame_surf = frames[frame_idx]

        # Apply slight bobbing when player is moving
        bob_x = math.sin(self.game.player.bob_timer * 0.008) * 8 if self.game.player.is_moving else 0
        bob_y = abs(math.cos(self.game.player.bob_timer * 0.008)) * 10 if self.game.player.is_moving else 0

        # Center weapon at bottom screen
        pos_x = HALF_WIDTH - frame_surf.get_width() // 2 + int(bob_x)
        pos_y = HEIGHT - frame_surf.get_height() + int(bob_y)

        # Draw reload lower offset
        if self.is_reloading:
            pos_y += 70

        screen.blit(frame_surf, (pos_x, pos_y))
