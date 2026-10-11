"""
Mission Debriefing & Game Over Modals:
Displays victory extraction statistics, survivor honors, leaderboard submission, and retry options.
"""
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, COLOR_WHITE, COLOR_GREEN, COLOR_BLOOD,
    COLOR_AMBER, COLOR_CYAN, COLOR_BLACK
)


class DebriefingModal:
    """Victory screen shown upon extracting with the rescued survivor."""
    def __init__(self, game):
        self.game = game
        self.font_hero = pg.font.SysFont("Arial", 32, bold=True)
        self.font_title = pg.font.SysFont("Arial", 22, bold=True)
        self.font_body = pg.font.SysFont("Arial", 16, bold=False)
        self.font_bold = pg.font.SysFont("Arial", 16, bold=True)

    def draw(self, screen):
        # Dark overlay
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((8, 10, 14, 230))
        screen.blit(overlay, (0, 0))

        # Modal Window
        box_w, box_h = 700, 520
        bx = (WIDTH - box_w) // 2
        by = (HEIGHT - box_h) // 2

        pg.draw.rect(screen, (20, 26, 34), (bx, by, box_w, box_h), border_radius=12)
        pg.draw.rect(screen, COLOR_GREEN, (bx, by, box_w, box_h), width=3, border_radius=12)

        # Header
        head = self.font_hero.render("MISSION ACCOMPLISHED: EXTRACTED!", True, COLOR_GREEN)
        screen.blit(head, head.get_rect(center=(WIDTH // 2, by + 45)))

        meta = self.game.level_map.meta
        sub = self.font_title.render(f"{meta['title']} Cleared", True, COLOR_WHITE)
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, by + 85)))

        # Survivor rescued card
        pg.draw.rect(screen, (15, 20, 26), (bx + 40, by + 120, box_w - 80, 95), border_radius=8)
        pg.draw.rect(screen, (40, 60, 50), (bx + 40, by + 120, box_w - 80, 95), width=2, border_radius=8)

        # Draw survivor avatar
        s_frames = self.game.asset_manager.survivor_sprites.get(self.game.level_map.level_id, [])
        if s_frames:
            thumb = pg.transform.scale(s_frames[0], (75, 75))
            screen.blit(thumb, (bx + 55, by + 130))

        res_tag = self.font_bold.render(f"VIP SURVIVOR RESCUED: {meta['survivor'].upper()}", True, COLOR_AMBER)
        screen.blit(res_tag, (bx + 145, by + 135))

        res_name = self.font_body.render(f"Name: {meta['survivor_name']} - {meta['survivor_bio']}", True, COLOR_WHITE)
        screen.blit(res_name, (bx + 145, by + 160))

        badge_txt = self.font_bold.render("★ SURVIVOR BADGE UNLOCKED & RECORDED", True, COLOR_GREEN)
        screen.blit(badge_txt, (bx + 145, by + 185))

        # Performance Stats
        elapsed = round(self.game.elapsed_time, 1)
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        kills = self.game.player.kills

        metrics = [
            ("Clearance Time", f"{mins:02d}:{secs:02d} ({elapsed} seconds)"),
            ("Zombies Neutralized", f"{kills} Infected Swarm"),
            ("Supabase Leaderboard", "Score submitted to global rank"),
            ("Firebase Cloud Sync", "Unlocked Next Quarantine Level (+250 Credits)"),
        ]

        for i, (label, val) in enumerate(metrics):
            my = by + 235 + i * 40
            l_surf = self.font_bold.render(label + ":", True, (160, 175, 190))
            v_surf = self.font_body.render(val, True, COLOR_WHITE)
            screen.blit(l_surf, (bx + 60, my))
            screen.blit(v_surf, (bx + 260, my))

        # Buttons
        # 1. Continue / Next Level
        btn_next = pg.Rect(bx + 60, by + box_h - 75, 260, 48)
        pg.draw.rect(screen, COLOR_GREEN, btn_next, border_radius=8)
        b1_txt = self.font_bold.render("NEXT MISSION", True, COLOR_BLACK)
        screen.blit(b1_txt, b1_txt.get_rect(center=btn_next.center))

        # 2. Return to Lobby
        btn_lobby = pg.Rect(bx + 380, by + box_h - 75, 260, 48)
        pg.draw.rect(screen, (35, 42, 55), btn_lobby, border_radius=8)
        pg.draw.rect(screen, (70, 85, 105), btn_lobby, width=2, border_radius=8)
        b2_txt = self.font_bold.render("LOBBY ARMORY", True, COLOR_WHITE)
        screen.blit(b2_txt, b2_txt.get_rect(center=btn_lobby.center))

    def handle_click(self, mx, my):
        box_w, box_h = 700, 520
        bx = (WIDTH - box_w) // 2
        by = (HEIGHT - box_h) // 2

        btn_next = pg.Rect(bx + 60, by + box_h - 75, 260, 48)
        btn_lobby = pg.Rect(bx + 380, by + box_h - 75, 260, 48)

        if btn_next.collidepoint(mx, my):
            next_lvl = min(5, self.game.level_map.level_id + 1)
            self.game.start_mission(next_lvl)
            return True
        elif btn_lobby.collidepoint(mx, my):
            self.game.return_to_lobby()
            return True
        return False


class GameOverModal:
    """Game over screen shown when player is defeated by the swarm."""
    def __init__(self, game):
        self.game = game
        self.font_hero = pg.font.SysFont("Arial", 36, bold=True)
        self.font_title = pg.font.SysFont("Arial", 22, bold=True)
        self.font_bold = pg.font.SysFont("Arial", 16, bold=True)

    def draw(self, screen):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((20, 5, 5, 240))
        screen.blit(overlay, (0, 0))

        head = self.font_hero.render("OPERATIVE KIA - MISSION FAILED", True, COLOR_BLOOD)
        screen.blit(head, head.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))

        sub = self.font_title.render("You were overrun by the infected swarm before extraction.", True, (220, 200, 200))
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

        # Retry button
        btn_retry = pg.Rect(WIDTH // 2 - 220, HEIGHT // 2 + 40, 200, 50)
        pg.draw.rect(screen, COLOR_BLOOD, btn_retry, border_radius=8)
        r_txt = self.font_bold.render("RETRY MISSION", True, COLOR_WHITE)
        screen.blit(r_txt, r_txt.get_rect(center=btn_retry.center))

        # Lobby button
        btn_lobby = pg.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 40, 200, 50)
        pg.draw.rect(screen, (35, 40, 50), btn_lobby, border_radius=8)
        l_txt = self.font_bold.render("RETURN TO LOBBY", True, COLOR_WHITE)
        screen.blit(l_txt, l_txt.get_rect(center=btn_lobby.center))

    def handle_click(self, mx, my):
        btn_retry = pg.Rect(WIDTH // 2 - 220, HEIGHT // 2 + 40, 200, 50)
        btn_lobby = pg.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 40, 200, 50)

        if btn_retry.collidepoint(mx, my):
            self.game.start_mission(self.game.level_map.level_id)
            return True
        elif btn_lobby.collidepoint(mx, my):
            self.game.return_to_lobby()
            return True
        return False
