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
        # Burst fire state (Assault rifle burst mode)
        self.burst_shots_remaining = 0
        self.next_burst_shot_time = 0
        self.burst_active_key = None
        # Active grenades in the level
        self.active_grenades = []

        # Smooth viewmodel bobbing interpolation
        self.bob_offset_x = 0.0
        self.bob_offset_y = 0.0

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
        self.burst_shots_remaining = 0
        self.burst_active_key = None
        self.game.sound_manager.play_reload()

    def select_weapon(self, weapon_name):
        if weapon_name in self.available_weapons:
            self.current_weapon_idx = self.available_weapons.index(weapon_name)
            self.current_weapon_key = weapon_name
            self.is_firing = False
            self.is_reloading = False
            self.anim_frame = 0
            self.burst_shots_remaining = 0
            self.burst_active_key = None

    def start_reload(self):
        clip, reserve = self.ammo_state[self.current_weapon_key]
        max_clip = self.current_config["max_ammo"]
        if self.is_reloading or clip >= max_clip or reserve <= 0:
            return
        self.is_reloading = True
        self.burst_shots_remaining = 0
        self.burst_active_key = None
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

    def _execute_single_shot(self, now):
        """Discharges a single bullet/shell for the active weapon."""
        clip, reserve = self.ammo_state[self.current_weapon_key]
        if clip <= 0:
            self.game.sound_manager.play_reload()
            self.start_reload()
            return False

        cfg = self.current_config

        # Deduct ammo
        self.ammo_state[self.current_weapon_key][0] -= 1
        self.last_shot_time = now
        self.is_firing = True
        self.anim_frame = 1  # Muzzle flash frame
        self.anim_timer = 50 if self.current_weapon_key == "rifle" else 90
        self.game.player.shots_fired += 1

        # Play weapon audio
        if self.current_weapon_key == "pistol":
            self.game.sound_manager.play_pistol()
        elif self.current_weapon_key == "shotgun":
            self.game.sound_manager.play_shotgun()
        elif self.current_weapon_key == "rifle":
            self.game.sound_manager.play_rifle()

        # Trigger object renderer muzzle flash
        flash_intensity = 80 if self.current_weapon_key == "rifle" else 100
        self.game.object_renderer.trigger_flash(flash_intensity)

        # Raycast Hitscan weapon trace
        pellets = cfg["pellets"]
        spread = cfg["spread"]
        dmg = cfg["damage"]
        max_range = cfg.get("range", 16.0)
        eff_range = cfg.get("effective_range", None)

        for _ in range(pellets):
            pellet_angle = self.game.player.angle + (random.random() * 2 - 1) * spread
            self.perform_hitscan(pellet_angle, dmg, max_range, eff_range)

        # Auto reload if empty
        if self.ammo_state[self.current_weapon_key][0] == 0:
            self.start_reload()

        return True

    def shoot(self):
        """Fires the weapon. If rifle (burst_count configured), queues and fires a 3-round burst."""
        now = pg.time.get_ticks()
        cfg = self.current_config

        # Do not fire if reloading or if mid-burst
        if self.is_reloading or self.burst_shots_remaining > 0:
            return False

        # Weapon-specific cooldown check
        fire_cooldown = cfg.get("burst_delay_ms", cfg["fire_rate_ms"])
        if (now - self.last_shot_time < fire_cooldown):
            return False

        clip, reserve = self.ammo_state[self.current_weapon_key]
        if clip <= 0:
            self.game.sound_manager.play_reload()
            self.start_reload()
            return False

        # Burst weapon (Assault Rifle) handling
        burst_count = cfg.get("burst_count", 1)
        if burst_count > 1:
            shots_available = min(burst_count, clip)
            # Fire first shot immediately
            fired = self._execute_single_shot(now)
            if fired:
                remaining_burst = shots_available - 1
                if remaining_burst > 0 and self.ammo_state[self.current_weapon_key][0] > 0 and not self.is_reloading:
                    self.burst_shots_remaining = remaining_burst
                    self.burst_active_key = self.current_weapon_key
                    self.next_burst_shot_time = now + cfg["fire_rate_ms"]
                return True
            return False

        # Single shot weapon (Pistol, Shotgun)
        return self._execute_single_shot(now)

    def perform_hitscan(self, angle, damage, max_range=16.0, effective_range=None):
        """Raycast hitscan check against all active zombies in player's field of fire within max_range."""
        hit_npc = None
        min_dist = float('inf')

        # Check all alive zombies
        for npc in self.game.sprite_manager.zombies:
            if not npc.alive:
                continue
            # Calculate angle and distance to zombie
            dx = npc.x - self.game.player.x
            dy = npc.y - self.game.player.y
            dist = math.hypot(dx, dy)

            # Range cutoff: ignore targets beyond this weapon's maximum range
            if dist > max_range:
                continue

            theta = math.atan2(dy, dx)
            delta = theta - angle
            # Normalize angle difference
            while delta > math.pi:
                delta -= math.tau
            while delta < -math.pi:
                delta += math.tau

            # Check if zombie is in front of the ray within angular tolerance
            angular_width = math.atan2(0.45, dist)  # Hitbox radius ~0.45 units
            if abs(delta) < angular_width:
                # Check for blocking wall between player and zombie
                if not self.check_wall_between(self.game.player.x, self.game.player.y, npc.x, npc.y):
                    if dist < min_dist:
                        min_dist = dist
                        hit_npc = npc

        if hit_npc:
            self.game.player.shots_hit += 1
            # Apply distance damage falloff between effective_range and max_range
            final_dmg = damage
            if effective_range and min_dist > effective_range:
                falloff_ratio = (min_dist - effective_range) / max(0.1, (max_range - effective_range))
                falloff_ratio = max(0.0, min(1.0, falloff_ratio))
                final_dmg = max(1, int(damage * (1.0 - 0.60 * falloff_ratio)))
            hit_npc.take_damage(final_dmg)

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

        # Process burst fire sequence for assault rifle
        if self.burst_shots_remaining > 0 and not self.is_reloading:
            if self.burst_active_key == self.current_weapon_key:
                if now >= self.next_burst_shot_time:
                    clip, _ = self.ammo_state[self.current_weapon_key]
                    if clip > 0:
                        self._execute_single_shot(now)
                        self.burst_shots_remaining -= 1
                        cfg = self.current_config
                        self.next_burst_shot_time = now + cfg["fire_rate_ms"]
                    else:
                        self.burst_shots_remaining = 0
            else:
                self.burst_shots_remaining = 0
                self.burst_active_key = None

        # Update firing viewmodel animation frame
        if self.is_firing:
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                self.anim_frame += 1
                frames = self.game.asset_manager.weapon_sprites.get(self.current_weapon_key, [])
                if self.anim_frame < len(frames):
                    self.anim_timer = 40 if self.current_weapon_key == "rifle" else 70
                else:
                    self.is_firing = False
                    self.anim_frame = 0

        # Update active grenades
        for g in list(self.active_grenades):
            g.update(dt)
            if g.exploded:
                self.active_grenades.remove(g)

    def draw_viewmodel(self, screen):
        """Draws first-person weapon viewmodel centered at the bottom of the screen with smooth sway."""
        # 1. Check if weapon is reloading and has dedicated animated reload frames
        reload_frames = getattr(self.game.asset_manager, "weapon_reload_sprites", {}).get(self.current_weapon_key, [])
        if self.is_reloading and reload_frames:
            reload_dur = self.current_config["reload_time_ms"]
            now = pg.time.get_ticks()
            elapsed = now - self.reload_start_time
            progress = max(0.0, min(0.999, elapsed / max(1.0, reload_dur)))
            r_idx = int(progress * len(reload_frames))
            frame_surf = reload_frames[r_idx]
        else:
            frames = self.game.asset_manager.weapon_sprites.get(self.current_weapon_key, [])
            if not frames:
                return
            frame_idx = min(self.anim_frame, len(frames) - 1)
            frame_surf = frames[frame_idx]

        # Calculate subtle, natural sway target
        if self.game.player.is_moving:
            amp = 7 if getattr(self.game.player, "is_running", False) else 5
            target_bob_x = math.sin(self.game.player.bob_timer * 0.005) * amp
            target_bob_y = abs(math.cos(self.game.player.bob_timer * 0.005)) * amp
        else:
            target_bob_x = 0.0
            target_bob_y = 0.0

        # Smooth exponential decay eliminates abrupt pops and snapping
        self.bob_offset_x += (target_bob_x - self.bob_offset_x) * 0.2
        self.bob_offset_y += (target_bob_y - self.bob_offset_y) * 0.2

        # Center weapon at bottom screen
        pos_x = HALF_WIDTH - frame_surf.get_width() // 2 + int(self.bob_offset_x)
        pos_y = HEIGHT - frame_surf.get_height() + int(self.bob_offset_y)

        # Draw reload lower offset only if weapon doesn't have animated reload sprites
        if self.is_reloading and not reload_frames:
            pos_y += 70

        screen.blit(frame_surf, (pos_x, pos_y))
