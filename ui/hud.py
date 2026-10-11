"""
In-Game Mobile HUD & Tactical Display:
Health/Armor gauges, Ammo counter, Minimap Radar, Objective Tracker, and Notifications.
"""
import math
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, COLOR_WHITE, COLOR_BLOOD, COLOR_AMBER,
    COLOR_CYAN, COLOR_GREEN, COLOR_PURPLE, COLOR_DARK_GRAY
)


class InGameHUD:
    def __init__(self, game):
        self.game = game
        self.font_title = pg.font.SysFont("Arial", 18, bold=True)
        self.font_hud = pg.font.SysFont("Arial", 16, bold=True)
        self.font_large = pg.font.SysFont("Arial", 28, bold=True)
        self.font_small = pg.font.SysFont("Arial", 13, bold=False)

        self.message_text = ""
        self.message_color = COLOR_WHITE
        self.message_timer = 0

    def show_message(self, text, color=COLOR_WHITE, duration_ms=2500):
        self.message_text = text
        self.message_color = color
        self.message_timer = duration_ms

    def show_dialog_rescue(self, level_id):
        meta = self.game.level_map.meta
        self.show_message(f"RESCUED {meta['survivor'].upper()} ({meta['survivor_name']})! EXTRACTION UNLOCKED!", COLOR_GREEN, 4500)

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message_text = ""

    def draw(self, screen):
        self.draw_top_bar(screen)
        self.draw_vitals(screen)
        self.draw_ammo_and_tactical(screen)
        self.draw_minimap(screen)
        self.draw_crosshair_and_prompts(screen)
        self.draw_message_banner(screen)

    def draw_top_bar(self, screen):
        # Translucent banner
        bar_surf = pg.Surface((WIDTH, 48), pg.SRCALPHA)
        bar_surf.fill((12, 14, 18, 200))
        pg.draw.line(bar_surf, (0, 210, 255, 120), (0, 47), (WIDTH, 47), 2)
        screen.blit(bar_surf, (0, 0))

        # Level Title
        meta = self.game.level_map.meta
        lvl_surf = self.font_title.render(f"{meta['title']} | {meta['subtitle']}", True, COLOR_CYAN)
        screen.blit(lvl_surf, (20, 12))

        # Objective Tracker in center
        if not self.game.level_map.survivor_rescued:
            obj_text = f"OBJECTIVE: RESCUE {meta['survivor'].upper()} ({meta['survivor_name']})"
            obj_col = COLOR_AMBER
        else:
            obj_text = "OBJECTIVE: REACH EVACUATION ZONE TO EXTRACT!"
            # Blinking green
            blink = int(time_blink := (pg.time.get_ticks() // 300) % 2)
            obj_col = COLOR_GREEN if blink else COLOR_WHITE

        obj_surf = self.font_hud.render(obj_text, True, obj_col)
        obj_rect = obj_surf.get_rect(center=(WIDTH // 2, 24))
        screen.blit(obj_surf, obj_rect)

        # Elapsed Timer
        elapsed_sec = int(self.game.elapsed_time)
        mins = elapsed_sec // 60
        secs = elapsed_sec % 60
        time_surf = self.font_title.render(f"TIME: {mins:02d}:{secs:02d}", True, COLOR_WHITE)
        screen.blit(time_surf, (WIDTH - 270, 12))

    def draw_vitals(self, screen):
        # Health & Armor Gauges (Lower Left)
        base_x = 20
        base_y = HEIGHT - 90

        # Background box
        box_surf = pg.Surface((250, 75), pg.SRCALPHA)
        box_surf.fill((15, 18, 22, 180))
        pg.draw.rect(box_surf, (50, 60, 75), (0, 0, 250, 75), 2)
        screen.blit(box_surf, (base_x, base_y))

        # Health bar
        hp = max(0, min(100, self.game.player.health))
        hp_col = COLOR_GREEN if hp > 50 else COLOR_AMBER if hp > 25 else COLOR_BLOOD
        pg.draw.rect(screen, (40, 20, 20), (base_x + 65, base_y + 12, 170, 20))
        pg.draw.rect(screen, hp_col, (base_x + 65, base_y + 12, int(1.7 * hp), 20))
        pg.draw.rect(screen, (80, 80, 80), (base_x + 65, base_y + 12, 170, 20), 1)

        hp_label = self.font_hud.render(f"HP: {hp}", True, COLOR_WHITE)
        screen.blit(hp_label, (base_x + 10, base_y + 12))

        # Armor bar
        armor = max(0, min(100, self.game.player.armor))
        pg.draw.rect(screen, (20, 35, 45), (base_x + 65, base_y + 42, 170, 20))
        pg.draw.rect(screen, COLOR_CYAN, (base_x + 65, base_y + 42, int(1.7 * armor), 20))
        pg.draw.rect(screen, (80, 80, 80), (base_x + 65, base_y + 42, 170, 20), 1)

        armor_label = self.font_hud.render(f"ARM: {armor}", True, COLOR_WHITE)
        screen.blit(armor_label, (base_x + 10, base_y + 42))

        # Adrenaline active indicator
        if self.game.player.adrenaline_active:
            ad_surf = self.font_small.render("STIM ACTIVE (+45% SPD)", True, (0, 240, 255))
            screen.blit(ad_surf, (base_x + 10, base_y - 22))

    def draw_ammo_and_tactical(self, screen):
        # Ammo counter & Weapon name (Lower Right)
        wm = self.game.weapon_manager
        cur_weapon = wm.current_weapon_key
        clip, reserve = wm.ammo_state[cur_weapon]
        cfg = wm.current_config

        box_x = WIDTH - 260
        box_y = HEIGHT - 85

        box_surf = pg.Surface((240, 75), pg.SRCALPHA)
        box_surf.fill((15, 18, 22, 180))
        pg.draw.rect(box_surf, (50, 60, 75), (0, 0, 240, 75), 2)
        screen.blit(box_surf, (box_x, box_y))

        # Weapon Name
        name_surf = self.font_hud.render(cfg["name"], True, COLOR_AMBER)
        screen.blit(name_surf, (box_x + 12, box_y + 10))

        # Ammo digits
        if wm.is_reloading:
            ammo_str = "RELOADING..."
            ammo_col = COLOR_AMBER
        else:
            ammo_str = f"{clip} / {reserve}"
            ammo_col = COLOR_WHITE if clip > 2 else COLOR_BLOOD

        ammo_surf = self.font_large.render(ammo_str, True, ammo_col)
        screen.blit(ammo_surf, (box_x + 12, box_y + 32))

        # Tactical Equipment Counts (Frag Grenades, Medkits, Keycards)
        inv = wm.inventory
        tact_surf = pg.Surface((220, 34), pg.SRCALPHA)
        tact_surf.fill((12, 14, 18, 190))
        pg.draw.rect(tact_surf, (40, 45, 55), (0, 0, 220, 34), 1)
        screen.blit(tact_surf, (box_x, box_y - 42))

        # Badges list
        cards_str = ",".join(k.upper() for k in inv["keycards"]) if inv["keycards"] else "NONE"
        tact_text = f"MED: {inv['medkit']} | GREN: {inv['grenade']} | KEY: {cards_str}"
        tact_label = self.font_small.render(tact_text, True, COLOR_WHITE)
        screen.blit(tact_label, (box_x + 10, box_y - 34))

    def draw_minimap(self, screen):
        # Minimap radar on Top-Right
        map_size = 110
        pos_x = WIDTH - map_size - 15
        pos_y = 56

        radar_surf = pg.Surface((map_size, map_size), pg.SRCALPHA)
        radar_surf.fill((10, 14, 18, 200))
        pg.draw.rect(radar_surf, (0, 210, 255, 140), (0, 0, map_size, map_size), 2)

        grid = self.game.level_map.grid
        rows = len(grid)
        cols = len(grid[0])
        cell_w = map_size / cols
        cell_h = map_size / rows

        # Draw walls
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if 1 <= cell <= 90:
                    pg.draw.rect(radar_surf, (70, 75, 85), (x * cell_w, y * cell_h, cell_w, cell_h))
                elif 101 <= cell <= 199:
                    # Door
                    door_open = self.game.level_map.door_positions.get((x, y), {}).get("open", False)
                    door_col = (40, 200, 80) if door_open else (230, 45, 45)
                    pg.draw.rect(radar_surf, door_col, (x * cell_w, y * cell_h, cell_w, cell_h))
                elif cell == 99:
                    # Extraction
                    pg.draw.rect(radar_surf, (0, 255, 120), (x * cell_w, y * cell_h, cell_w, cell_h))

        # Draw Survivor
        sx, sy = self.game.level_map.survivor_pos
        s_col = (255, 230, 40)
        pg.draw.circle(radar_surf, s_col, (int(sx * cell_w), int(sy * cell_h)), 3)

        # Draw Zombies
        for z in self.game.sprite_manager.zombies:
            if z.alive:
                pg.draw.circle(radar_surf, (240, 30, 30), (int(z.x * cell_w), int(z.y * cell_h)), 2)

        # Draw Player & View Cone
        px, py = self.game.player.x, self.game.player.y
        p_screen = (int(px * cell_w), int(py * cell_h))
        pg.draw.circle(radar_surf, (0, 220, 255), p_screen, 3)

        # View cone
        p_angle = self.game.player.angle
        line_len = 10
        end_x = p_screen[0] + int(math.cos(p_angle) * line_len)
        end_y = p_screen[1] + int(math.sin(p_angle) * line_len)
        pg.draw.line(radar_surf, (0, 220, 255), p_screen, (end_x, end_y), 2)

        screen.blit(radar_surf, (pos_x, pos_y))

    def draw_crosshair_and_prompts(self, screen):
        # Draw dynamic center crosshair
        ch = self.game.asset_manager.crosshair
        screen.blit(ch, (WIDTH // 2 - 24, HEIGHT // 2 - 24))

        # Contextual Interaction Prompts
        p = self.game.player
        prompt_text = ""
        prompt_col = COLOR_WHITE

        if p.near_survivor and not p.near_survivor.rescued:
            prompt_text = "PRESS ACTION TO RESCUE SURVIVOR"
            prompt_col = COLOR_GREEN
        elif p.near_door:
            card = p.near_door[1]
            has_card = card in self.game.weapon_manager.inventory["keycards"]
            prompt_text = f"PRESS ACTION TO UNLOCK ({card.upper()})" if has_card else f"DOOR LOCKED: REQUIRES {card.upper()} KEYCARD"
            prompt_col = COLOR_GREEN if has_card else COLOR_BLOOD
        elif p.near_extraction:
            if self.game.level_map.extraction_unlocked:
                prompt_text = "EXTRACTION PAD: EVACUATE NOW!"
                prompt_col = COLOR_GREEN
            else:
                prompt_text = "EXTRACTION LOCKED: RESCUE SURVIVOR FIRST"
                prompt_col = COLOR_AMBER

        if prompt_text:
            p_surf = self.font_hud.render(prompt_text, True, prompt_col)
            p_rect = p_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55))
            # Dark backing
            back = pg.Surface((p_rect.width + 20, p_rect.height + 10), pg.SRCALPHA)
            back.fill((10, 12, 16, 210))
            screen.blit(back, (p_rect.x - 10, p_rect.y - 5))
            screen.blit(p_surf, p_rect)

    def draw_message_banner(self, screen):
        if self.message_text:
            m_surf = self.font_title.render(self.message_text, True, self.message_color)
            m_rect = m_surf.get_rect(center=(WIDTH // 2, 85))
            back = pg.Surface((m_rect.width + 30, m_rect.height + 12), pg.SRCALPHA)
            back.fill((14, 16, 20, 220))
            pg.draw.rect(back, self.message_color, (0, 0, m_rect.width + 30, m_rect.height + 12), 2)
            screen.blit(back, (m_rect.x - 15, m_rect.y - 6))
            screen.blit(m_surf, m_rect)
