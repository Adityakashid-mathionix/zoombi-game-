"""
Authentic Retro DOOM-Style FPS HUD & Status Bar:
Embossed DOOM status bar with authentic DOOM pixel digits for Health, Armor, and Ammo,
Illuminated keycard slots, Tactical equipment loadout, Compact CRT radar, and Clean Radio Comms.
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
        self.font_title = pg.font.SysFont("Arial", 16, bold=True)
        self.font_hud = pg.font.SysFont("Arial", 14, bold=True)
        self.font_bold = pg.font.SysFont("Arial", 13, bold=True)
        self.font_small = pg.font.SysFont("Arial", 11, bold=True)

        self.message_text = ""
        self.message_color = COLOR_WHITE
        self.message_timer = 0
        self.radar_sweep_angle = 0.0

        # Load authentic DOOM digits from asset_manager or directly from assets/textures/digits
        self.digit_images = getattr(self.game.asset_manager, "digit_textures", {})

    def show_message(self, text, color=COLOR_WHITE, duration_ms=3000):
        self.message_text = text
        self.message_color = color
        self.message_timer = duration_ms

    def show_dialog_rescue(self, level_id):
        meta = self.game.level_map.meta
        self.show_message(
            f"★ RESCUED {meta['survivor'].upper()}! EXTRACTION GATE UNLOCKED! ★",
            COLOR_GREEN, 4500
        )

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message_text = ""

        # Smooth radar sweep
        self.radar_sweep_angle = (self.radar_sweep_angle + dt * 0.0035) % math.tau

    def draw(self, screen):
        self.draw_top_bar(screen)
        self.draw_bottom_status_bar(screen)
        self.draw_minimap(screen)
        self.draw_crosshair_and_prompts(screen)
        self.draw_radio_comms_banner(screen)
        self.draw_critical_health_vignette(screen)

    def draw_top_bar(self, screen):
        # Sleek, minimalist top header strip (36 px tall)
        top_h = 36
        top_surf = pg.Surface((WIDTH, top_h), pg.SRCALPHA)
        top_surf.fill((12, 16, 22, 225))
        pg.draw.line(top_surf, (55, 65, 80), (0, top_h - 1), (WIDTH, top_h - 1), 2)
        screen.blit(top_surf, (0, 0))

        # Sector Name with Biohazard Emblem
        meta = self.game.level_map.meta
        lvl_num = getattr(self.game.level_map, "level_id", 1)
        sec_text = f"☣ SECTOR 0{lvl_num}: {meta['title'].upper()}"
        sec_surf = self.font_hud.render(sec_text, True, COLOR_CYAN)
        screen.blit(sec_surf, (20, 9))

        # Centered Mission Objective
        if not self.game.level_map.survivor_rescued:
            obj_text = f"OBJECTIVE: RESCUE {meta['survivor'].upper()} ({meta['survivor_name']})"
            obj_col = COLOR_AMBER
        else:
            obj_text = "★ EXTRACTION UNLOCKED: ESCORT SURVIVOR TO EVAC PAD ★"
            blink = (pg.time.get_ticks() // 280) % 2
            obj_col = COLOR_GREEN if blink else COLOR_WHITE

        obj_surf = self.font_hud.render(obj_text, True, obj_col)
        obj_rect = obj_surf.get_rect(center=(WIDTH // 2, 18))
        screen.blit(obj_surf, obj_rect)

        # Elapsed Timer & Threat Count
        elapsed_sec = int(self.game.elapsed_time)
        mins = elapsed_sec // 60
        secs = elapsed_sec % 60
        alive_zombies = sum(1 for z in self.game.sprite_manager.zombies if z.alive)
        stat_text = f"ENEMIES: {alive_zombies} | {mins:02d}:{secs:02d}"
        stat_surf = self.font_hud.render(stat_text, True, (230, 235, 240))
        screen.blit(stat_surf, (WIDTH - 250, 9))

    def draw_doom_digits(self, surface, number_val, x, y, has_percent=False):
        """Renders integer using authentic DOOM red/gold pixel digits."""
        num_str = str(number_val)
        cur_x = x
        for ch in num_str:
            if ch in self.digit_images:
                img = self.digit_images[ch]
                surface.blit(img, (cur_x, y))
                cur_x += img.get_width() - 4
            else:
                # Fallback font render if image missing
                fallback = self.font_title.render(ch, True, (255, 215, 40))
                surface.blit(fallback, (cur_x, y + 8))
                cur_x += 16

        if has_percent and "10" in self.digit_images:
            pct_img = self.digit_images["10"]
            surface.blit(pct_img, (cur_x, y))

    def draw_bottom_status_bar(self, screen):
        # Classic DOOM status bar anchored along bottom
        bar_h = 72
        bar_y = HEIGHT - bar_h

        # Status Bar Chassis
        bar_surf = pg.Surface((WIDTH, bar_h))
        bar_surf.fill((16, 18, 24))
        # Top bevel trim
        pg.draw.line(bar_surf, (70, 80, 95), (0, 0), (WIDTH, 0), 3)
        pg.draw.line(bar_surf, (30, 35, 45), (0, 3), (WIDTH, 3), 1)

        # 1. AMMO MODULE (x: 40 .. 280)
        pg.draw.rect(bar_surf, (10, 12, 16), (40, 8, 230, 56))
        pg.draw.rect(bar_surf, (45, 55, 70), (40, 8, 230, 56), 2)

        wm = self.game.weapon_manager
        cur_weapon = wm.current_weapon_key
        clip, reserve = wm.ammo_state[cur_weapon]
        cfg = wm.current_config

        lbl_ammo = self.font_small.render(f"AMMO // {cfg['name'].upper()}", True, COLOR_AMBER)
        bar_surf.blit(lbl_ammo, (50, 12))

        if wm.is_reloading:
            reloading_text = self.font_title.render("RELOADING...", True, COLOR_AMBER)
            bar_surf.blit(reloading_text, (52, 30))
        else:
            self.draw_doom_digits(bar_surf, f"{clip:02d}", 50, 26)
            res_surf = self.font_hud.render(f"/ {reserve}", True, (180, 190, 205))
            bar_surf.blit(res_surf, (135, 36))

        # 2. HEALTH MODULE (x: 290 .. 530)
        pg.draw.rect(bar_surf, (10, 12, 16), (290, 8, 230, 56))
        pg.draw.rect(bar_surf, (45, 55, 70), (290, 8, 230, 56), 2)

        hp = max(0, min(100, self.game.player.health))
        hp_lbl_col = (50, 230, 90) if hp > 30 else (240, 40, 40)
        lbl_hp = self.font_small.render("BIO-HEALTH", True, hp_lbl_col)
        bar_surf.blit(lbl_hp, (300, 12))

        self.draw_doom_digits(bar_surf, hp, 300, 26, has_percent=True)

        # Small heart / pulse icon or text
        pulse_txt = "HEART: STABLE" if hp > 40 else "HEART: CRITICAL"
        pulse_surf = self.font_small.render(pulse_txt, True, hp_lbl_col)
        bar_surf.blit(pulse_surf, (430, 16))

        # 3. ARMOR MODULE (x: 540 .. 780)
        pg.draw.rect(bar_surf, (10, 12, 16), (540, 8, 230, 56))
        pg.draw.rect(bar_surf, (45, 55, 70), (540, 8, 230, 56), 2)

        armor = max(0, min(100, self.game.player.armor))
        lbl_arm = self.font_small.render("ARMOR / KEVLAR", True, COLOR_CYAN)
        bar_surf.blit(lbl_arm, (550, 12))

        self.draw_doom_digits(bar_surf, armor, 550, 26, has_percent=True)

        if self.game.player.adrenaline_active:
            ad_lbl = self.font_small.render("STIM BOOST", True, (0, 240, 255))
            bar_surf.blit(ad_lbl, (680, 16))

        # 4. KEYCARDS & TACTICAL SUPPLIES (x: 790 .. 1240)
        pg.draw.rect(bar_surf, (10, 12, 16), (790, 8, 450, 56))
        pg.draw.rect(bar_surf, (45, 55, 70), (790, 8, 450, 56), 2)

        lbl_keys = self.font_small.render("KEYCARDS // TACTICAL GEAR", True, (240, 240, 245))
        bar_surf.blit(lbl_keys, (800, 12))

        # Render acquired Keycards with illuminated card badges
        inv = wm.inventory
        acquired_keys = inv["keycards"]
        card_colors = [
            ("red", (240, 45, 45)),
            ("yellow", (250, 215, 30)),
            ("blue", (40, 150, 255)),
            ("green", (45, 220, 80)),
            ("purple", (190, 60, 245)),
            ("orange", (255, 130, 25)),
            ("crimson", (220, 25, 45)),
            ("gold", (245, 215, 30)),
        ]
        card_x = 800
        for k_name, k_col in card_colors:
            has_it = k_name in acquired_keys
            # Draw card slot
            box_col = k_col if has_it else (35, 40, 48)
            border_col = (255, 255, 255) if has_it else (60, 65, 75)
            pg.draw.rect(bar_surf, box_col, (card_x, 32, 22, 26), border_radius=3)
            pg.draw.rect(bar_surf, border_col, (card_x, 32, 22, 26), 1, border_radius=3)
            if has_it:
                dot = self.font_small.render(k_name[0].upper(), True, (10, 10, 15))
                bar_surf.blit(dot, (card_x + 6, 36))
            card_x += 27

        # Tactical Supplies Badges
        tact_x = 1030
        med_txt = self.font_hud.render(f"MED: {inv['medkit']}", True, (50, 225, 100))
        gren_txt = self.font_hud.render(f"FRAG: {inv['grenade']}", True, (255, 140, 30))
        stim_txt = self.font_hud.render(f"STIM: {inv['stim']}", True, COLOR_CYAN)
        bar_surf.blit(med_txt, (tact_x, 32))
        bar_surf.blit(gren_txt, (tact_x + 75, 32))
        bar_surf.blit(stim_txt, (tact_x + 155, 32))

        screen.blit(bar_surf, (0, bar_y))

    def draw_minimap(self, screen):
        # Compact top-right CRT radar scanner (95 x 95 px)
        map_size = 95
        pos_x = WIDTH - map_size - 15
        pos_y = 44

        radar_surf = pg.Surface((map_size, map_size), pg.SRCALPHA)
        radar_surf.fill((8, 14, 12, 215))

        grid = self.game.level_map.grid
        rows = len(grid)
        cols = len(grid[0])
        cell_w = map_size / cols
        cell_h = map_size / rows

        # Draw level map walls & doors
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if 1 <= cell <= 90:
                    pg.draw.rect(radar_surf, (45, 55, 50), (x * cell_w, y * cell_h, cell_w, cell_h))
                elif 101 <= cell <= 199:
                    door_open = self.game.level_map.door_positions.get((x, y), {}).get("open", False)
                    door_col = (40, 220, 90) if door_open else (230, 45, 45)
                    pg.draw.rect(radar_surf, door_col, (x * cell_w, y * cell_h, cell_w, cell_h))
                elif cell == 99:
                    pg.draw.rect(radar_surf, (0, 255, 140), (x * cell_w, y * cell_h, cell_w, cell_h))

        # Rotating CRT sweep beam
        center_x = map_size // 2
        center_y = map_size // 2
        sweep_x = center_x + int(math.cos(self.radar_sweep_angle) * (map_size * 0.70))
        sweep_y = center_y + int(math.sin(self.radar_sweep_angle) * (map_size * 0.70))
        pg.draw.line(radar_surf, (50, 255, 120, 160), (center_x, center_y), (sweep_x, sweep_y), 1)

        # Draw Survivor as golden blip
        sx, sy = self.game.level_map.survivor_pos
        s_col = (255, 225, 40)
        pg.draw.circle(radar_surf, s_col, (int(sx * cell_w), int(sy * cell_h)), 3)

        # Draw Zombies as red threat dots
        for z in self.game.sprite_manager.zombies:
            if z.alive:
                pg.draw.circle(radar_surf, (245, 35, 35), (int(z.x * cell_w), int(z.y * cell_h)), 2)

        # Draw Player dot & view pointer
        px, py = self.game.player.x, self.game.player.y
        p_screen = (int(px * cell_w), int(py * cell_h))
        pg.draw.circle(radar_surf, (0, 220, 255), p_screen, 3)

        p_angle = self.game.player.angle
        line_len = 10
        end_x = p_screen[0] + int(math.cos(p_angle) * line_len)
        end_y = p_screen[1] + int(math.sin(p_angle) * line_len)
        pg.draw.line(radar_surf, (0, 220, 255), p_screen, (end_x, end_y), 2)

        # Radar border
        pg.draw.rect(radar_surf, (45, 180, 95, 190), (0, 0, map_size, map_size), 2)
        screen.blit(radar_surf, (pos_x, pos_y))

    def draw_radio_comms_banner(self, screen):
        # Display transmission messages cleanly at top
        if self.message_text:
            m_surf = self.font_hud.render(self.message_text, True, self.message_color)
            m_rect = m_surf.get_rect(center=(WIDTH // 2, 54))
            back = pg.Surface((m_rect.width + 30, m_rect.height + 12), pg.SRCALPHA)
            back.fill((14, 18, 24, 235))
            pg.draw.rect(back, self.message_color, (0, 0, m_rect.width + 30, m_rect.height + 12), 2)
            screen.blit(back, (m_rect.x - 15, m_rect.y - 6))
            screen.blit(m_surf, m_rect)

    def draw_crosshair_and_prompts(self, screen):
        # Center combat crosshair
        ch = self.game.asset_manager.crosshair
        screen.blit(ch, (WIDTH // 2 - 24, HEIGHT // 2 - 24))

        # Contextual interaction prompts
        p = self.game.player
        prompt_text = ""
        prompt_col = COLOR_WHITE

        if p.near_survivor and not p.near_survivor.rescued:
            prompt_text = "★ PRESS E / ACTION TO RESCUE SURVIVOR ★"
            prompt_col = COLOR_GREEN
        elif p.near_door:
            card = p.near_door[1]
            has_card = card in self.game.weapon_manager.inventory["keycards"]
            prompt_text = f"PRESS E / ACTION TO UNLOCK ({card.upper()})" if has_card else f"DOOR LOCKED: REQUIRES {card.upper()} KEYCARD"
            prompt_col = COLOR_GREEN if has_card else COLOR_BLOOD
        elif p.near_extraction:
            if self.game.level_map.extraction_unlocked:
                prompt_text = "★ EVACUATION ZONE: PROCEED TO COMPLETE MISSION ★"
                prompt_col = COLOR_GREEN
            else:
                prompt_text = "EXTRACTION LOCKED: RESCUE SURVIVOR FIRST"
                prompt_col = COLOR_AMBER

        if prompt_text:
            p_surf = self.font_hud.render(prompt_text, True, prompt_col)
            p_rect = p_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 52))
            back = pg.Surface((p_rect.width + 24, p_rect.height + 10), pg.SRCALPHA)
            back.fill((12, 16, 22, 225))
            pg.draw.rect(back, prompt_col, (0, 0, p_rect.width + 24, p_rect.height + 10), 2)
            screen.blit(back, (p_rect.x - 12, p_rect.y - 5))
            screen.blit(p_surf, p_rect)

    def draw_critical_health_vignette(self, screen):
        # Subtle pulsing vignette when health < 25
        hp = self.game.player.health
        if hp < 25:
            alpha = int(40 + 30 * math.sin(pg.time.get_ticks() * 0.008))
            vignette = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            pg.draw.rect(vignette, (180, 15, 25, alpha), (0, 0, WIDTH, HEIGHT), 6)
            screen.blit(vignette, (0, 0))
