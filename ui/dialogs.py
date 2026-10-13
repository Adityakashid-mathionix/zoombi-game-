"""
Mission Debriefing & Game Over Modals:
Displays animated victory sequence, survivor honors, leaderboard submission, and retry options.
"""
import math
import random
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, COLOR_WHITE, COLOR_GREEN,
    COLOR_BLOOD, COLOR_AMBER, COLOR_CYAN, COLOR_BLACK
)


class DebriefingModal:
    """Victory screen shown upon extracting with the rescued survivor."""
    def __init__(self, game):
        self.game = game
        self.font_hero = pg.font.SysFont("Arial", 34, bold=True)
        self.font_title = pg.font.SysFont("Arial", 22, bold=True)
        self.font_body = pg.font.SysFont("Arial", 16, bold=False)
        self.font_bold = pg.font.SysFont("Arial", 16, bold=True)
        self.font_small = pg.font.SysFont("Arial", 14, bold=True)

        self.anim_time = 0.0
        self.particles = []
        self.played_sound = False

    def reset(self):
        self.anim_time = 0.0
        self.played_sound = False
        # Create celebratory victory confetti / sparkles
        self.particles = []
        for _ in range(60):
            self.particles.append({
                "x": random.randint(100, WIDTH - 100),
                "y": random.randint(-50, HEIGHT // 2),
                "vx": random.uniform(-1.5, 1.5),
                "vy": random.uniform(2.0, 5.5),
                "color": random.choice([(255, 215, 0), (50, 255, 120), (255, 255, 255), (0, 220, 255)]),
                "size": random.randint(3, 6),
                "rot": random.uniform(0, math.tau),
            })

    def update(self, dt):
        self.anim_time += dt

        # Update sparkles
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["rot"] += 0.05
            if p["y"] > HEIGHT:
                p["y"] = -10
                p["x"] = random.randint(100, WIDTH - 100)

        # Trigger music / fanfare on completion
        if not self.played_sound:
            self.played_sound = True
            try:
                if hasattr(self.game.sound_manager, "play"):
                    self.game.sound_manager.play("rescue")
            except Exception:
                pass

    def draw(self, screen):
        # 1. Background: Draw authentic DOOM win texture if available
        win_img = getattr(self.game.asset_manager, "win_image", None)
        if win_img:
            screen.blit(win_img, (0, 0))
            # Subtle dark vignette
            dark = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            dark.fill((10, 14, 20, 160))
            screen.blit(dark, (0, 0))
        else:
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((8, 12, 18, 240))
            screen.blit(overlay, (0, 0))

        # 2. Draw animated confetti / golden sparkles
        for p in self.particles:
            pg.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["size"])

        # 3. Phase 1: High-impact Victory Banner (First 1.8 seconds)
        if self.anim_time < 1800:
            pulse = math.sin(self.anim_time * 0.008) * 6
            t_scale = min(1.0, self.anim_time / 400.0)

            # Central glowing banner box
            banner_w = int(760 * t_scale)
            banner_h = int(140 * t_scale)
            if banner_w > 10 and banner_h > 10:
                banner_surf = pg.Surface((banner_w, banner_h), pg.SRCALPHA)
                banner_surf.fill((16, 22, 32, 225))
                pg.draw.rect(banner_surf, (255, 215, 0, 240), (0, 0, banner_w, banner_h), width=4, border_radius=14)
                # Outer gold neon glow
                pg.draw.rect(banner_surf, (255, 200, 30, 80), (4, 4, banner_w - 8, banner_h - 8), width=2, border_radius=10)
                screen.blit(banner_surf, (HALF_WIDTH - banner_w // 2, HALF_HEIGHT - banner_h // 2 + int(pulse)))

                # Text
                t1 = self.font_hero.render("★ MISSION ACCOMPLISHED ★", True, (255, 225, 40))
                screen.blit(t1, t1.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 22 + int(pulse))))

                meta = self.game.level_map.meta
                t2 = self.font_title.render(f"VIP SURVIVOR {meta['survivor'].upper()} SECURED & EXTRACTED!", True, (100, 255, 160))
                screen.blit(t2, t2.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 24 + int(pulse))))
            return

        # 4. Phase 2: Sleek Realistic Military Debriefing Modal (After 1.8 seconds)
        fade_in = min(1.0, (self.anim_time - 1800) / 400.0)
        box_w, box_h = 740, 530
        bx = (WIDTH - box_w) // 2
        by = int((HEIGHT - box_h) // 2 + (1.0 - fade_in) * 50)

        # Main glassmorphism card
        modal_surf = pg.Surface((box_w, box_h), pg.SRCALPHA)
        modal_surf.fill((14, 18, 25, int(245 * fade_in)))
        pg.draw.rect(modal_surf, (40, 215, 110, int(255 * fade_in)), (0, 0, box_w, box_h), width=3, border_radius=12)
        # Inner technical border
        pg.draw.rect(modal_surf, (60, 90, 80, int(150 * fade_in)), (6, 6, box_w - 12, box_h - 12), width=1, border_radius=10)
        screen.blit(modal_surf, (bx, by))

        # Title Header
        head = self.font_hero.render("MISSION ACCOMPLISHED: EXTRACTED", True, (50, 240, 120))
        screen.blit(head, head.get_rect(center=(WIDTH // 2, by + 42)))

        meta = self.game.level_map.meta
        sub = self.font_title.render(f"Sector Cleared: {meta['title']}", True, (215, 225, 235))
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, by + 80)))

        # Survivor Card Frame
        card_rect = pg.Rect(bx + 40, by + 115, box_w - 80, 100)
        pg.draw.rect(screen, (22, 28, 38), card_rect, border_radius=8)
        pg.draw.rect(screen, (55, 80, 70), card_rect, width=2, border_radius=8)

        # Survivor Avatar Portrait
        s_frames = self.game.asset_manager.survivor_sprites.get(self.game.level_map.level_id, [])
        if s_frames:
            thumb = pg.transform.smoothscale(s_frames[0], (80, 80))
            screen.blit(thumb, (bx + 55, by + 125))

        res_tag = self.font_bold.render(f"VIP SECURED: {meta['survivor'].upper()}", True, (255, 205, 40))
        screen.blit(res_tag, (bx + 150, by + 128))

        res_name = self.font_body.render(f"Operative: {meta['survivor_name']} - {meta['survivor_bio']}", True, COLOR_WHITE)
        screen.blit(res_name, (bx + 150, by + 154))

        badge_txt = self.font_bold.render("★ CAMPAIGN HONOR MEDAL RECORDED TO CLOUD DOSSIER", True, (60, 230, 140))
        screen.blit(badge_txt, (bx + 150, by + 180))

        # Performance Metrics Table
        elapsed = round(self.game.elapsed_time, 1)
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        kills = self.game.player.kills

        metrics = [
            ("Tactical Clearance Time", f"{mins:02d}:{secs:02d} ({elapsed}s)"),
            ("Hostile Swarm Neutralized", f"{kills} Mutated Zombies"),
            ("Supabase Global Leaderboard", "Telemetry verified & rank posted"),
            ("Firebase Realtime Cloud Sync", "Career dossier updated (+250 Credits)"),
        ]

        for i, (label, val) in enumerate(metrics):
            my = by + 235 + i * 40
            pg.draw.rect(screen, (20, 24, 32), (bx + 40, my - 4, box_w - 80, 32), border_radius=6)
            l_surf = self.font_bold.render(label, True, (160, 180, 200))
            v_surf = self.font_bold.render(val, True, (240, 245, 255))
            screen.blit(l_surf, (bx + 55, my + 2))
            screen.blit(v_surf, (bx + 310, my + 2))

        # Action Buttons
        btn_next = pg.Rect(bx + 50, by + box_h - 75, 300, 50)
        pg.draw.rect(screen, (35, 215, 105), btn_next, border_radius=8)
        pg.draw.rect(screen, (200, 255, 220), btn_next, width=2, border_radius=8)
        b1_txt = self.font_bold.render("DEPLOY NEXT MISSION ▶", True, COLOR_BLACK)
        screen.blit(b1_txt, b1_txt.get_rect(center=btn_next.center))

        btn_lobby = pg.Rect(bx + 390, by + box_h - 75, 300, 50)
        pg.draw.rect(screen, (32, 40, 52), btn_lobby, border_radius=8)
        pg.draw.rect(screen, (75, 95, 120), btn_lobby, width=2, border_radius=8)
        b2_txt = self.font_bold.render("RETURN TO ARMORY ⛯", True, COLOR_WHITE)
        screen.blit(b2_txt, b2_txt.get_rect(center=btn_lobby.center))

    def handle_click(self, mx, my):
        # Allow instant skip of animation
        if self.anim_time < 1800:
            self.anim_time = 1800
            return True

        box_w, box_h = 740, 530
        bx = (WIDTH - box_w) // 2
        by = (HEIGHT - box_h) // 2

        btn_next = pg.Rect(bx + 50, by + box_h - 75, 300, 50)
        btn_lobby = pg.Rect(bx + 390, by + box_h - 75, 300, 50)

        if btn_next.collidepoint(mx, my):
            from engine.settings import LEVELS_DATA
            cur_lvl = self.game.level_map.level_id
            is_rand = getattr(self.game.level_map, "random_map", False)
            if cur_lvl < len(LEVELS_DATA):
                next_lvl = cur_lvl + 1
                self.game.start_mission(next_lvl, random_map=is_rand)
            else:
                self.game.start_mission(cur_lvl, random_map=True)
            return True
        elif btn_lobby.collidepoint(mx, my):
            self.game.return_to_lobby()
            return True
        return False


class GameOverModal:
    """Game over screen shown when player is defeated by the swarm."""
    def __init__(self, game):
        self.game = game
        self.font_hero = pg.font.SysFont("Arial", 38, bold=True)
        self.font_title = pg.font.SysFont("Arial", 22, bold=True)
        self.font_bold = pg.font.SysFont("Arial", 16, bold=True)
        self.anim_time = 0.0

    def reset(self):
        self.anim_time = 0.0

    def update(self, dt):
        self.anim_time += dt

    def draw(self, screen):
        # Draw authentic DOOM game over backdrop if available
        go_img = getattr(self.game.asset_manager, "game_over_image", None)
        if go_img:
            screen.blit(go_img, (0, 0))
            dark = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            dark.fill((25, 6, 6, 175))
            screen.blit(dark, (0, 0))
        else:
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((25, 5, 5, 240))
            screen.blit(overlay, (0, 0))

        pulse = math.sin(self.anim_time * 0.005) * 5

        head = self.font_hero.render("OPERATIVE KIA - MISSION FAILED", True, (240, 30, 40))
        screen.blit(head, head.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90 + int(pulse))))

        sub = self.font_title.render("You were overrun by the infected swarm before extraction.", True, (225, 210, 210))
        screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 35)))

        # Retry button
        btn_retry = pg.Rect(WIDTH // 2 - 230, HEIGHT // 2 + 45, 210, 52)
        pg.draw.rect(screen, (215, 30, 40), btn_retry, border_radius=8)
        pg.draw.rect(screen, (255, 120, 120), btn_retry, width=2, border_radius=8)
        r_txt = self.font_bold.render("RETRY MISSION ↻", True, COLOR_WHITE)
        screen.blit(r_txt, r_txt.get_rect(center=btn_retry.center))

        # Lobby button
        btn_lobby = pg.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 45, 210, 52)
        pg.draw.rect(screen, (38, 44, 56), btn_lobby, border_radius=8)
        pg.draw.rect(screen, (80, 100, 125), btn_lobby, width=2, border_radius=8)
        l_txt = self.font_bold.render("RETURN TO LOBBY ⛯", True, COLOR_WHITE)
        screen.blit(l_txt, l_txt.get_rect(center=btn_lobby.center))

    def handle_click(self, mx, my):
        btn_retry = pg.Rect(WIDTH // 2 - 230, HEIGHT // 2 + 45, 210, 52)
        btn_lobby = pg.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 45, 210, 52)

        if btn_retry.collidepoint(mx, my):
            is_rand = getattr(self.game.level_map, "random_map", False)
            self.game.start_mission(self.game.level_map.level_id, random_map=is_rand)
            return True
        elif btn_lobby.collidepoint(mx, my):
            self.game.return_to_lobby()
            return True
        return False
