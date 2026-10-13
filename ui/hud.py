"""
In-Game Zombie Apocalypse HUD & Tactical Bio-Monitor:
Biohazard quarantine telemetry, Animated ECG Heart Rate Monitor, Motion-Tracking Radar,
Survivor Distress Beacon frequency tracker, and Proximity Threat Warning System.
"""
import math
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, COLOR_WHITE, COLOR_BLOOD, COLOR_AMBER,
    COLOR_CYAN, COLOR_GREEN, COLOR_PURPLE, COLOR_DARK_GRAY,
    COLOR_YELLOW, COLOR_GOLD
)


class InGameHUD:
    def __init__(self, game):
        self.game = game
        self.font_title = pg.font.SysFont("Arial", 18, bold=True)
        self.font_hud = pg.font.SysFont("Arial", 16, bold=True)
        self.font_large = pg.font.SysFont("Arial", 28, bold=True)
        self.font_small = pg.font.SysFont("Arial", 12, bold=False)
        self.font_tiny = pg.font.SysFont("Arial", 11, bold=True)

        self.message_text = ""
        self.message_color = COLOR_WHITE
        self.message_timer = 0
        self.radar_sweep_angle = 0.0

        # Pre-calculated ECG waveform cache
        self.ecg_time = 0.0

    def show_message(self, text, color=COLOR_WHITE, duration_ms=2500):
        self.message_text = text
        self.message_color = color
        self.message_timer = duration_ms

    def show_dialog_rescue(self, level_id):
        meta = self.game.level_map.meta
        self.show_message(
            f"★ RESCUED {meta['survivor'].upper()} ({meta['survivor_name']})! EXTRACTION ZONE UNLOCKED! ★",
            COLOR_GREEN, 5000
        )

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message_text = ""

        # Update radar sweep angle (smooth rotation)
        self.radar_sweep_angle = (self.radar_sweep_angle + dt * 0.0035) % math.tau

        # Update ECG heart rate timer
        # Heart beats faster when health is low or zombies are near
        hp = self.game.player.health
        bpm_speed = 0.006 if hp > 50 else 0.010 if hp > 25 else 0.016
        self.ecg_time += dt * bpm_speed

    def draw(self, screen):
        self.draw_top_bar(screen)
        self.draw_vitals(screen)
        self.draw_ammo_and_tactical(screen)
        self.draw_minimap(screen)
        self.draw_distress_and_proximity_alerts(screen)
        self.draw_crosshair_and_prompts(screen)
        self.draw_message_banner(screen)
        self.draw_critical_health_vignette(screen)

    def _draw_hazard_stripes(self, surface, rect, stripe_w=12, col1=(230, 185, 30), col2=(20, 20, 25)):
        """Draws classic black-and-yellow industrial hazard warning chevron stripes."""
        rx, ry, rw, rh = rect
        surf = pg.Surface((rw, rh), pg.SRCALPHA)
        surf.fill(col1)
        # Draw diagonal slashes
        for i in range(-rh, rw + rh, stripe_w * 2):
            pts = [(i, 0), (i + stripe_w, 0), (i + stripe_w - rh, rh), (i - rh, rh)]
            pg.draw.polygon(surf, col2, pts)
        surface.blit(surf, (rx, ry))

    def draw_top_bar(self, screen):
        # 1. Industrial bunker header banner
        bar_h = 50
        bar_surf = pg.Surface((WIDTH, bar_h), pg.SRCALPHA)
        bar_surf.fill((10, 14, 18, 230))
        screen.blit(bar_surf, (0, 0))

        # Bottom hazard warning stripe border
        self._draw_hazard_stripes(screen, (0, bar_h - 4, WIDTH, 4), stripe_w=10, col1=(255, 180, 20), col2=(20, 20, 25))

        # Level / Sector Title with Biohazard Emblem
        meta = self.game.level_map.meta
        lvl_num = getattr(self.game.level_map, "level_id", 1)
        difficulty_tag = f"DEFCON {max(1, 5 - lvl_num)}"
        lvl_text = f"☣ SECTOR 0{lvl_num}: {meta['title']} [{difficulty_tag}]"
        lvl_surf = self.font_hud.render(lvl_text, True, COLOR_CYAN)
        screen.blit(lvl_surf, (18, 14))

        # Objective Tracker with glowing warning state
        if not self.game.level_map.survivor_rescued:
            obj_text = f"☣ OBJECTIVE: RESCUE {meta['survivor'].upper()} ({meta['survivor_name']}) ☣"
            obj_col = COLOR_AMBER
        else:
            obj_text = "★ OBJECTIVE: ESCORT SURVIVOR TO EXTRACTION GATE ★"
            blink = (pg.time.get_ticks() // 280) % 2
            obj_col = COLOR_GREEN if blink else COLOR_WHITE

        obj_surf = self.font_hud.render(obj_text, True, obj_col)
        obj_rect = obj_surf.get_rect(center=(WIDTH // 2, 24))
        # Subtle backing glow for objective
        obj_bg = pg.Surface((obj_rect.width + 16, obj_rect.height + 6), pg.SRCALPHA)
        obj_bg.fill((20, 25, 32, 190))
        pg.draw.rect(obj_bg, obj_col, (0, 0, obj_rect.width + 16, obj_rect.height + 6), 1)
        screen.blit(obj_bg, (obj_rect.x - 8, obj_rect.y - 3))
        screen.blit(obj_surf, obj_rect)

        # Elapsed Timer & Zombie Threat Counter (Top Right)
        elapsed_sec = int(self.game.elapsed_time)
        mins = elapsed_sec // 60
        secs = elapsed_sec % 60
        alive_zombies = sum(1 for z in self.game.sprite_manager.zombies if z.alive)
        
        stat_text = f"INFECTED: {alive_zombies} | TIME: {mins:02d}:{secs:02d}"
        stat_surf = self.font_hud.render(stat_text, True, (245, 230, 210))
        screen.blit(stat_surf, (WIDTH - 275, 14))

    def draw_vitals(self, screen):
        # Top-Left Bio-Monitor Gauge (avoiding mobile virtual joystick at bottom-left)
        base_x = 18
        base_y = 58
        box_w = 245
        box_h = 82

        # Distressed metal chassis
        chassis = pg.Surface((box_w, box_h), pg.SRCALPHA)
        chassis.fill((12, 15, 20, 220))
        pg.draw.rect(chassis, (55, 65, 80), (0, 0, box_w, box_h), 2)
        # Hazard accent tab on upper corner
        pg.draw.rect(chassis, (255, 180, 25), (0, 0, 36, 4))
        screen.blit(chassis, (base_x, base_y))

        # Health & Heart Rate Calculation
        hp = max(0, min(100, self.game.player.health))
        hp_col = COLOR_GREEN if hp > 50 else COLOR_AMBER if hp > 25 else COLOR_BLOOD
        calculated_bpm = int(72 + (100 - hp) * 0.75 + (15 if self.game.player.adrenaline_active else 0))

        # Small CRT Waveform Monitor box (38x26 px)
        ecg_x = base_x + 8
        ecg_y = base_y + 12
        ecg_surf = pg.Surface((44, 28))
        ecg_surf.fill((6, 12, 8))
        pg.draw.rect(ecg_surf, (20, 45, 25), (0, 0, 44, 28), 1)

        # Draw live ECG waveform trace
        ecg_points = []
        for i in range(44):
            t_wave = (self.ecg_time + i * 0.15) % math.tau
            # ECG spike synthesis (P-Q-R-S-T)
            spike = 0.0
            if 1.4 < t_wave < 1.9:
                spike = math.sin((t_wave - 1.4) * 6.28) * 11
            elif 2.6 < t_wave < 3.0:
                spike = -math.sin((t_wave - 2.6) * 7.8) * 4
            py = 14 - int(spike)
            py = max(2, min(26, py))
            ecg_points.append((i, py))

        if len(ecg_points) > 1:
            line_col = (50, 255, 100) if hp > 30 else (255, 45, 45)
            pg.draw.lines(ecg_surf, line_col, False, ecg_points, 1)
        screen.blit(ecg_surf, (ecg_x, ecg_y))

        # BPM text under waveform
        bpm_label = self.font_tiny.render(f"{calculated_bpm} BPM", True, hp_col)
        screen.blit(bpm_label, (ecg_x + 2, ecg_y + 30))

        # Health Bar (Segmented Bio-Vitals)
        bar_x = base_x + 60
        bar_w = 172
        pg.draw.rect(screen, (30, 15, 18), (bar_x, base_y + 10, bar_w, 16))
        fill_hp_w = int((bar_w * hp) / 100)
        pg.draw.rect(screen, hp_col, (bar_x, base_y + 10, fill_hp_w, 16))
        # Segment dividers
        for s in range(1, 10):
            pg.draw.line(screen, (10, 10, 15), (bar_x + int(s * (bar_w / 10)), base_y + 10), (bar_x + int(s * (bar_w / 10)), base_y + 25), 1)
        pg.draw.rect(screen, (75, 85, 100), (bar_x, base_y + 10, bar_w, 16), 1)

        hp_txt = self.font_small.render(f"BIO-VITALS: {hp}%", True, COLOR_WHITE)
        screen.blit(hp_txt, (bar_x + 6, base_y + 11))

        # Armor Bar (Hazmat Rig)
        armor = max(0, min(100, self.game.player.armor))
        pg.draw.rect(screen, (15, 25, 35), (bar_x, base_y + 32, bar_w, 16))
        fill_arm_w = int((bar_w * armor) / 100)
        pg.draw.rect(screen, COLOR_CYAN, (bar_x, base_y + 32, fill_arm_w, 16))
        for s in range(1, 10):
            pg.draw.line(screen, (10, 10, 15), (bar_x + int(s * (bar_w / 10)), base_y + 32), (bar_x + int(s * (bar_w / 10)), base_y + 47), 1)
        pg.draw.rect(screen, (75, 85, 100), (bar_x, base_y + 32, bar_w, 16), 1)

        arm_txt = self.font_small.render(f"HAZMAT RIG: {armor}%", True, COLOR_WHITE)
        screen.blit(arm_txt, (bar_x + 6, base_y + 33))

        # Adrenaline Stim Shot active banner
        if self.game.player.adrenaline_active:
            ad_surf = self.font_tiny.render("⚡ STIM ACTIVE (+45% SPEED)", True, (0, 245, 255))
            screen.blit(ad_surf, (bar_x + 6, base_y + 54))
        elif hp < 25:
            alert_surf = self.font_tiny.render("☣ CRITICAL INFECTION - USE MEDKIT", True, COLOR_BLOOD)
            screen.blit(alert_surf, (bar_x + 6, base_y + 54))

    def draw_ammo_and_tactical(self, screen):
        # Top-Right Munitions & Tactical Loadout (below radar minimap)
        wm = self.game.weapon_manager
        cur_weapon = wm.current_weapon_key
        clip, reserve = wm.ammo_state[cur_weapon]
        cfg = wm.current_config

        box_x = WIDTH - 235
        box_y = 188
        box_w = 220
        box_h = 70

        # Bunker ammo panel
        box_surf = pg.Surface((box_w, box_h), pg.SRCALPHA)
        box_surf.fill((12, 15, 20, 220))
        pg.draw.rect(box_surf, (55, 65, 80), (0, 0, box_w, box_h), 2)
        # Hazard accent tab
        pg.draw.rect(box_surf, (220, 30, 40), (box_w - 36, 0, 36, 4))
        screen.blit(box_surf, (box_x, box_y))

        # Weapon Name
        name_surf = self.font_hud.render(f"☠ {cfg['name']}", True, COLOR_AMBER)
        screen.blit(name_surf, (box_x + 10, box_y + 8))

        # Ammo readouts
        if wm.is_reloading:
            ammo_str = "RELOADING..."
            ammo_col = COLOR_AMBER
        else:
            ammo_str = f"{clip:02d} / {reserve:02d}"
            ammo_col = COLOR_WHITE if clip > 2 else COLOR_BLOOD

        ammo_surf = self.font_large.render(ammo_str, True, ammo_col)
        screen.blit(ammo_surf, (box_x + 10, box_y + 28))

        # Tactical Equipment Counts (Frag Grenades, Medkits, Keycards)
        inv = wm.inventory
        tact_surf = pg.Surface((box_w, 26), pg.SRCALPHA)
        tact_surf.fill((10, 12, 16, 230))
        pg.draw.rect(tact_surf, (45, 50, 60), (0, 0, box_w, 26), 1)
        screen.blit(tact_surf, (box_x, box_y + 74))

        cards_str = ",".join(k.upper() for k in inv["keycards"]) if inv["keycards"] else "NONE"
        tact_text = f"MED: {inv['medkit']} | GREN: {inv['grenade']} | KEY: {cards_str}"
        tact_label = self.font_small.render(tact_text, True, (230, 235, 240))
        screen.blit(tact_label, (box_x + 8, box_y + 79))

    def draw_minimap(self, screen):
        # Top-Right CRT Bio-Scanner Radar
        map_size = 120
        pos_x = WIDTH - map_size - 15
        pos_y = 58

        radar_surf = pg.Surface((map_size, map_size), pg.SRCALPHA)
        radar_surf.fill((8, 14, 12, 225))

        grid = self.game.level_map.grid
        rows = len(grid)
        cols = len(grid[0])
        cell_w = map_size / cols
        cell_h = map_size / rows

        # Draw map geometry
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if 1 <= cell <= 90:
                    pg.draw.rect(radar_surf, (45, 60, 50), (x * cell_w, y * cell_h, cell_w, cell_h))
                elif 101 <= cell <= 199:
                    # Door
                    door_open = self.game.level_map.door_positions.get((x, y), {}).get("open", False)
                    door_col = (40, 220, 90) if door_open else (230, 45, 45)
                    pg.draw.rect(radar_surf, door_col, (x * cell_w, y * cell_h, cell_w, cell_h))
                elif cell == 99:
                    # Extraction point
                    pg.draw.rect(radar_surf, (0, 255, 140), (x * cell_w, y * cell_h, cell_w, cell_h))

        # Rotating Radar Sweep line
        center_x = map_size // 2
        center_y = map_size // 2
        sweep_end_x = center_x + int(math.cos(self.radar_sweep_angle) * (map_size * 0.70))
        sweep_end_y = center_y + int(math.sin(self.radar_sweep_angle) * (map_size * 0.70))
        pg.draw.line(radar_surf, (50, 255, 120, 160), (center_x, center_y), (sweep_end_x, sweep_end_y), 1)

        # Draw Trapped/Rescued Survivor
        sx, sy = self.game.level_map.survivor_pos
        s_col = (255, 225, 40)
        # Pulsing blip
        s_radius = 3 + int((pg.time.get_ticks() // 250) % 2)
        pg.draw.circle(radar_surf, s_col, (int(sx * cell_w), int(sy * cell_h)), s_radius)

        # Draw Zombies as red threat blips
        for z in self.game.sprite_manager.zombies:
            if z.alive:
                pg.draw.circle(radar_surf, (245, 30, 30), (int(z.x * cell_w), int(z.y * cell_h)), 2)

        # Draw Player & Direction Pointer
        px, py = self.game.player.x, self.game.player.y
        p_screen = (int(px * cell_w), int(py * cell_h))
        pg.draw.circle(radar_surf, (0, 220, 255), p_screen, 3)

        p_angle = self.game.player.angle
        line_len = 11
        end_x = p_screen[0] + int(math.cos(p_angle) * line_len)
        end_y = p_screen[1] + int(math.sin(p_angle) * line_len)
        pg.draw.line(radar_surf, (0, 220, 255), p_screen, (end_x, end_y), 2)

        # High-tech circular or framed reticle
        pg.draw.rect(radar_surf, (40, 180, 90, 180), (0, 0, map_size, map_size), 2)
        radar_label = self.font_tiny.render("BIO-SCANNER", True, (50, 230, 110))
        radar_surf.blit(radar_label, (4, 4))

        screen.blit(radar_surf, (pos_x, pos_y))

    def draw_distress_and_proximity_alerts(self, screen):
        # 1. Trapped Survivor Distress Beacon Alert
        survivor = self.game.sprite_manager.survivor
        if survivor and not survivor.rescued:
            dist_s = math.hypot(self.game.player.x - survivor.x, self.game.player.y - survivor.y)
            if dist_s <= 7.0:
                # Pulsing Distress Signal Header Banner
                b_w = 460
                b_h = 32
                b_x = HALF_WIDTH - b_w // 2
                b_y = 56

                beacon_surf = pg.Surface((b_w, b_h), pg.SRCALPHA)
                beacon_surf.fill((25, 18, 10, 210))
                pg.draw.rect(beacon_surf, (255, 190, 30), (0, 0, b_w, b_h), 2)

                # Sound frequency bar visualizer
                now = pg.time.get_ticks()
                wave_val = abs(math.sin(now * 0.009))
                msg_txt = f"📻 [SOS 142.8 MHz] SURVIVOR CALLING: \"HELP!\" (DIST: {dist_s:.1f}m)"
                label = self.font_small.render(msg_txt, True, (255, 215, 60))
                beacon_surf.blit(label, (14, 8))
                screen.blit(beacon_surf, (b_x, b_y))

        # 2. Zombie Melee Proximity Warning
        # Check closest living zombie
        closest_dist = 999.0
        for z in self.game.sprite_manager.zombies:
            if z.alive:
                d = math.hypot(self.game.player.x - z.x, self.game.player.y - z.y)
                if d < closest_dist:
                    closest_dist = d

        if closest_dist < 2.8:
            # Flashing red proximity warning
            blink = (pg.time.get_ticks() // 200) % 2
            if blink:
                w_w = 400
                w_h = 28
                w_x = HALF_WIDTH - w_w // 2
                w_y = HEIGHT - 80

                warn_surf = pg.Surface((w_w, w_h), pg.SRCALPHA)
                warn_surf.fill((45, 10, 15, 230))
                pg.draw.rect(warn_surf, (255, 30, 40), (0, 0, w_w, w_h), 2)
                txt = self.font_hud.render("⚠ DANGER: INFECTED IN STRIKE RANGE ⚠", True, (255, 220, 220))
                warn_surf.blit(txt, txt.get_rect(center=(w_w // 2, w_h // 2)))
                screen.blit(warn_surf, (w_x, w_y))

    def draw_critical_health_vignette(self, screen):
        # Pulsing bloody border when health is critically low (< 25%)
        hp = self.game.player.health
        if hp < 25:
            alpha = int(45 + 35 * math.sin(pg.time.get_ticks() * 0.008))
            vignette = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            pg.draw.rect(vignette, (200, 15, 25, alpha), (0, 0, WIDTH, HEIGHT), 8)
            pg.draw.rect(vignette, (160, 10, 20, alpha // 2), (8, 8, WIDTH - 16, HEIGHT - 16), 14)
            screen.blit(vignette, (0, 0))

    def draw_crosshair_and_prompts(self, screen):
        # Center combat crosshair
        ch = self.game.asset_manager.crosshair
        screen.blit(ch, (WIDTH // 2 - 24, HEIGHT // 2 - 24))

        # Contextual Interaction Prompts
        p = self.game.player
        prompt_text = ""
        prompt_col = COLOR_WHITE

        if p.near_survivor and not p.near_survivor.rescued:
            prompt_text = "★ PRESS ACTION TO RESCUE SURVIVOR ★"
            prompt_col = COLOR_GREEN
        elif p.near_door:
            card = p.near_door[1]
            has_card = card in self.game.weapon_manager.inventory["keycards"]
            prompt_text = f"PRESS ACTION TO UNLOCK ({card.upper()})" if has_card else f"DOOR LOCKED: REQUIRES {card.upper()} KEYCARD"
            prompt_col = COLOR_GREEN if has_card else COLOR_BLOOD
        elif p.near_extraction:
            if self.game.level_map.extraction_unlocked:
                prompt_text = "★ EXTRACTION PAD: EVACUATE NOW! ★"
                prompt_col = COLOR_GREEN
            else:
                prompt_text = "EXTRACTION LOCKED: RESCUE SURVIVOR FIRST"
                prompt_col = COLOR_AMBER

        if prompt_text:
            p_surf = self.font_hud.render(prompt_text, True, prompt_col)
            p_rect = p_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 58))
            back = pg.Surface((p_rect.width + 24, p_rect.height + 12), pg.SRCALPHA)
            back.fill((10, 14, 18, 225))
            pg.draw.rect(back, prompt_col, (0, 0, p_rect.width + 24, p_rect.height + 12), 2)
            screen.blit(back, (p_rect.x - 12, p_rect.y - 6))
            screen.blit(p_surf, p_rect)

    def draw_message_banner(self, screen):
        if self.message_text:
            m_surf = self.font_title.render(self.message_text, True, self.message_color)
            m_rect = m_surf.get_rect(center=(WIDTH // 2, 98))
            back = pg.Surface((m_rect.width + 34, m_rect.height + 14), pg.SRCALPHA)
            back.fill((12, 16, 22, 235))
            pg.draw.rect(back, self.message_color, (0, 0, m_rect.width + 34, m_rect.height + 14), 2)
            screen.blit(back, (m_rect.x - 17, m_rect.y - 7))
            screen.blit(m_surf, m_rect)
