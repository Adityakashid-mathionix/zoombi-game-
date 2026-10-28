"""
Main Menu & Equipment Lobby:
Loadout Selection, Campaign Level Selector (1-5), Operative Stats/Badges,
Supabase Global Leaderboards, and Firebase Cloud Sync.
"""
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, LEVELS_DATA, WEAPON_CONFIGS, TACTICAL_CONFIGS,
    COLOR_WHITE, COLOR_BLOOD, COLOR_AMBER, COLOR_CYAN, COLOR_GREEN,
    COLOR_PURPLE, COLOR_DARK_GRAY, COLOR_BLACK, get_font
)


class LobbyMenu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.current_tab = "campaign"  # campaign, loadout, profile, leaderboards, settings

        # Safe Fonts guaranteed to load on Android
        self.font_hero = get_font(36, bold=True)
        self.font_title = get_font(22, bold=True)
        self.font_body = get_font(16, bold=False)
        self.font_bold = get_font(16, bold=True)
        self.font_small = get_font(13, bold=False)

        # Selected level in selector (1 to 8)
        self.selected_level_id = 1
        self.random_map_mode = False
        self.campaign_page = 0  # 0: Levels 1-4, 1: Levels 5-8

        # Selected primary weapon and tactical item
        self.selected_primary = self.game.firebase_service.cache["loadout"]["primary_weapon"]
        self.selected_tactical = self.game.firebase_service.cache["loadout"]["tactical_item"]

        # Leaderboard filter
        self.leaderboard_level = 1

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            self.process_click(mx, my)

        # Touch screen compatibility
        elif event.type == pg.FINGERDOWN:
            mx = int(event.x * WIDTH)
            my = int(event.y * HEIGHT)
            self.process_click(mx, my)

        # Keyboard shortcuts in lobby
        elif event.type == pg.KEYDOWN:
            if event.key in (pg.K_RETURN, pg.K_SPACE):
                self.game.start_mission(
                    self.selected_level_id, self.selected_primary, self.selected_tactical,
                    random_map=self.random_map_mode
                )
            elif event.key in (pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8):
                lvl = event.key - pg.K_0
                if lvl in self.game.firebase_service.cache.get("unlocked_levels", [1]):
                    self.selected_level_id = lvl
                    self.campaign_page = 0 if lvl <= 4 else 1
            elif event.key == pg.K_r:
                # Toggle Random Map Generator mode
                self.random_map_mode = not self.random_map_mode
            elif event.key in (pg.K_p, pg.K_LEFT, pg.K_RIGHT):
                # Switch page
                self.campaign_page = 1 - self.campaign_page
            elif event.key == pg.K_TAB:
                # Cycle tabs
                tab_order = ["campaign", "loadout", "profile", "leaderboards", "settings"]
                cur_i = tab_order.index(self.current_tab) if self.current_tab in tab_order else 0
                self.current_tab = tab_order[(cur_i + 1) % len(tab_order)]

    def process_click(self, mx, my):
        # 1. Top Navigation Tabs
        tabs = [
            ("campaign", "CAMPAIGN DEPLOY", 160),
            ("loadout", "ARMORY / LOADOUT", 370),
            ("profile", "OPERATIVE STATS", 580),
            ("leaderboards", "LEADERBOARD", 790),
            ("settings", "SETTINGS", 1000),
        ]
        if 20 <= my <= 65:
            for tab_id, label, tab_x in tabs:
                if tab_x - 90 <= mx <= tab_x + 90:
                    self.current_tab = tab_id
                    return

        # 2. Content Clicks based on active tab
        if self.current_tab == "campaign":
            self.handle_campaign_clicks(mx, my)
        elif self.current_tab == "loadout":
            self.handle_loadout_clicks(mx, my)
        elif self.current_tab == "leaderboards":
            self.handle_leaderboard_clicks(mx, my)

    def handle_campaign_clicks(self, mx, my):
        # 1. Page Selector Buttons at top (y = 86..118)
        p1_rect = pg.Rect(70, 86, 170, 32)
        p2_rect = pg.Rect(255, 86, 170, 32)
        if p1_rect.collidepoint(mx, my):
            self.campaign_page = 0
            return
        if p2_rect.collidepoint(mx, my):
            self.campaign_page = 1
            return

        # 2. Random Map Generator Toggle Button (Top Right)
        mode_rect = pg.Rect(WIDTH - 380, 86, 310, 32)
        if mode_rect.collidepoint(mx, my):
            self.random_map_mode = not self.random_map_mode
            return

        # 3. Check level card clicks (4 cards on current page)
        card_w, card_h = 260, 370
        start_x = 70
        y = 130
        page_start = self.campaign_page * 4 + 1
        unlocked_levels = self.game.firebase_service.cache.get("unlocked_levels", [1])

        for idx in range(4):
            lvl_id = page_start + idx
            x = start_x + idx * 290
            if x <= mx <= x + card_w and y <= my <= y + card_h:
                if lvl_id in unlocked_levels:
                    self.selected_level_id = lvl_id
                return

        # 4. Action buttons at bottom
        # Quick Random Map button (Left)
        quick_rand_rect = pg.Rect(70, HEIGHT - 110, 260, 55)
        if quick_rand_rect.collidepoint(mx, my):
            self.random_map_mode = True
            self.game.start_mission(
                self.selected_level_id, self.selected_primary, self.selected_tactical,
                random_map=True
            )
            return

        # Center Main DEPLOY Button
        deploy_rect = pg.Rect(WIDTH // 2 - 170, HEIGHT - 110, 340, 55)
        if deploy_rect.collidepoint(mx, my):
            self.game.start_mission(
                self.selected_level_id, self.selected_primary, self.selected_tactical,
                random_map=self.random_map_mode
            )
            return

        # Map Mode Toggle (Right)
        toggle_btn = pg.Rect(WIDTH - 330, HEIGHT - 110, 260, 55)
        if toggle_btn.collidepoint(mx, my):
            self.random_map_mode = not self.random_map_mode
            return

    def handle_loadout_clicks(self, mx, my):
        # Primary weapons selection
        w_options = ["shotgun", "rifle", "pistol"]
        for i, w_key in enumerate(w_options):
            r = pg.Rect(80 + i * 360, 160, 320, 150)
            if r.collidepoint(mx, my):
                self.selected_primary = w_key
                self.game.firebase_service.set_loadout(self.selected_primary, self.selected_tactical)

        # Tactical equipment selection
        t_options = ["medkit", "grenade", "stim"]
        for i, t_key in enumerate(t_options):
            r = pg.Rect(80 + i * 360, 380, 320, 150)
            if r.collidepoint(mx, my):
                self.selected_tactical = t_key
                self.game.firebase_service.set_loadout(self.selected_primary, self.selected_tactical)

    def handle_leaderboard_clicks(self, mx, my):
        # Level filter tabs at y=135 for levels 1 to 8
        for lvl_id in range(1, 9):
            bx = 120 + (lvl_id - 1) * 135
            if bx - 55 <= mx <= bx + 55 and 130 <= my <= 175:
                self.leaderboard_level = lvl_id

    def draw(self):
        self.screen.fill(COLOR_BLACK)

        # Background subtle grid pattern
        for x in range(0, WIDTH, 64):
            pg.draw.line(self.screen, (20, 22, 28), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 64):
            pg.draw.line(self.screen, (20, 22, 28), (0, y), (WIDTH, y))

        # Top Navigation Bar
        self.draw_navigation_bar()

        # Render Active Tab Content
        if self.current_tab == "campaign":
            self.draw_campaign_tab()
        elif self.current_tab == "loadout":
            self.draw_loadout_tab()
        elif self.current_tab == "profile":
            self.draw_profile_tab()
        elif self.current_tab == "leaderboards":
            self.draw_leaderboard_tab()
        elif self.current_tab == "settings":
            self.draw_settings_tab()

    def draw_navigation_bar(self):
        nav_surf = pg.Surface((WIDTH, 75), pg.SRCALPHA)
        nav_surf.fill((14, 16, 22, 240))
        pg.draw.line(nav_surf, (0, 210, 255, 140), (0, 74), (WIDTH, 74), 2)
        self.screen.blit(nav_surf, (0, 0))

        tabs = [
            ("campaign", "CAMPAIGN DEPLOY", 160),
            ("loadout", "ARMORY / LOADOUT", 370),
            ("profile", "OPERATIVE STATS", 580),
            ("leaderboards", "LEADERBOARD", 790),
            ("settings", "SETTINGS", 1000),
        ]

        for tab_id, label, tab_x in tabs:
            is_active = (self.current_tab == tab_id)
            col = COLOR_CYAN if is_active else (160, 170, 185)

            if is_active:
                pg.draw.rect(self.screen, (0, 210, 255, 60), (tab_x - 85, 18, 170, 42), border_radius=6)
                pg.draw.rect(self.screen, COLOR_CYAN, (tab_x - 85, 18, 170, 42), width=2, border_radius=6)

            text = self.font_bold.render(label, True, col)
            self.screen.blit(text, text.get_rect(center=(tab_x, 39)))

        # Status badge (Cloud Sync indicator)
        is_cloud = self.game.firebase_service.is_connected or self.game.supabase_service.is_connected
        status_text = "ONLINE CLOUD SYNC" if is_cloud else "LOCAL CACHED"
        status_col = COLOR_GREEN if is_cloud else COLOR_AMBER
        st_surf = self.font_small.render(status_text, True, status_col)
        self.screen.blit(st_surf, (WIDTH - 150, 30))

    def draw_campaign_tab(self):
        # 1. Top Controls Bar: Page Selectors & Random Map Mode Toggle
        # Page 1 button
        p1_active = (self.campaign_page == 0)
        p1_rect = pg.Rect(70, 86, 170, 32)
        pg.draw.rect(self.screen, (0, 210, 255, 60) if p1_active else (25, 28, 35), p1_rect, border_radius=6)
        pg.draw.rect(self.screen, COLOR_CYAN if p1_active else (55, 60, 70), p1_rect, width=2 if p1_active else 1, border_radius=6)
        p1_txt = self.font_bold.render("SECTORS 1 - 4", True, COLOR_CYAN if p1_active else (150, 160, 170))
        self.screen.blit(p1_txt, p1_txt.get_rect(center=p1_rect.center))

        # Page 2 button
        p2_active = (self.campaign_page == 1)
        p2_rect = pg.Rect(255, 86, 170, 32)
        pg.draw.rect(self.screen, (0, 210, 255, 60) if p2_active else (25, 28, 35), p2_rect, border_radius=6)
        pg.draw.rect(self.screen, COLOR_CYAN if p2_active else (55, 60, 70), p2_rect, width=2 if p2_active else 1, border_radius=6)
        p2_txt = self.font_bold.render("SECTORS 5 - 8", True, COLOR_CYAN if p2_active else (150, 160, 170))
        self.screen.blit(p2_txt, p2_txt.get_rect(center=p2_rect.center))

        # Random Map Generator Mode Toggle Button (Top Right)
        mode_rect = pg.Rect(WIDTH - 390, 86, 320, 32)
        mode_bg = (40, 25, 55) if self.random_map_mode else (20, 35, 45)
        mode_border = COLOR_PURPLE if self.random_map_mode else COLOR_CYAN
        pg.draw.rect(self.screen, mode_bg, mode_rect, border_radius=6)
        pg.draw.rect(self.screen, mode_border, mode_rect, width=2, border_radius=6)

        mode_label = "🎲 MAP: PROCEDURAL RANDOM [ON]" if self.random_map_mode else "📜 MAP: CLASSIC CAMPAIGN [ON]"
        mode_col = COLOR_PURPLE if self.random_map_mode else COLOR_CYAN
        mode_surf = self.font_bold.render(mode_label, True, mode_col)
        self.screen.blit(mode_surf, mode_surf.get_rect(center=mode_rect.center))

        # 2. Level Cards (4 cards across screen on current page)
        card_w, card_h = 260, 370
        start_x = 70
        y = 130
        page_start = self.campaign_page * 4 + 1
        unlocked_levels = self.game.firebase_service.cache.get("unlocked_levels", [1])

        for idx in range(4):
            lvl_id = page_start + idx
            x = start_x + idx * 290
            is_unlocked = (lvl_id in unlocked_levels)
            is_selected = (self.selected_level_id == lvl_id)
            meta = LEVELS_DATA[lvl_id]

            # Card background
            card_surf = pg.Surface((card_w, card_h), pg.SRCALPHA)
            bg_col = (25, 30, 42, 230) if is_unlocked else (15, 16, 20, 210)
            card_surf.fill(bg_col)

            border_col = COLOR_CYAN if is_selected else (0, 180, 220) if is_unlocked else (50, 55, 65)
            border_w = 3 if is_selected else 1
            pg.draw.rect(card_surf, border_col, (0, 0, card_w, card_h), width=border_w, border_radius=8)
            self.screen.blit(card_surf, (x, y))

            # Status Tag
            status_text = "CLEARED" if (lvl_id + 1 in unlocked_levels) else "UNLOCKED" if is_unlocked else "LOCKED"
            status_col = COLOR_GREEN if status_text == "CLEARED" else COLOR_AMBER if is_unlocked else (120, 125, 135)
            st_surf = self.font_small.render(status_text, True, status_col)
            self.screen.blit(st_surf, (x + 14, y + 14))

            # Random mode tag on card
            if self.random_map_mode and is_unlocked:
                r_tag = self.font_small.render("[PROCEDURAL]", True, COLOR_PURPLE)
                self.screen.blit(r_tag, (x + card_w - 95, y + 14))

            # Level Header
            title_surf = self.font_bold.render(f"LEVEL {lvl_id}", True, COLOR_WHITE)
            self.screen.blit(title_surf, (x + 14, y + 36))

            lvl_name = meta["title"].split(": ")[1] if ": " in meta["title"] else meta["title"]
            name_surf = self.font_small.render(lvl_name[:26], True, (200, 210, 225))
            self.screen.blit(name_surf, (x + 14, y + 60))

            # Survivor Card Box
            pg.draw.rect(self.screen, (15, 18, 24), (x + 12, y + 95, card_w - 24, 135), border_radius=6)
            pg.draw.rect(self.screen, (40, 48, 60), (x + 12, y + 95, card_w - 24, 135), width=1, border_radius=6)

            # Survivor avatar
            s_frames = self.game.asset_manager.survivor_sprites.get(lvl_id, [])
            if s_frames and is_unlocked:
                thumb = pg.transform.scale(s_frames[0], (70, 70))
                self.screen.blit(thumb, (x + (card_w - 70) // 2, y + 105))
            else:
                lock_text = self.font_bold.render("[LOCKED]" if not is_unlocked else "[VIP]", True, (130, 140, 150))
                self.screen.blit(lock_text, lock_text.get_rect(center=(x + card_w // 2, y + 140)))

            s_name = self.font_small.render(f"VIP: {meta['survivor']}", True, COLOR_AMBER if is_unlocked else (90, 95, 105))
            self.screen.blit(s_name, s_name.get_rect(center=(x + card_w // 2, y + 185)))

            doc_name = self.font_small.render(meta['survivor_name'], True, COLOR_WHITE if is_unlocked else (70, 75, 80))
            self.screen.blit(doc_name, doc_name.get_rect(center=(x + card_w // 2, y + 205)))

            # Keycard details
            kc_col = meta.get('keycard_color', COLOR_AMBER)
            kc_surf = self.font_small.render(f"Key: {meta['keycard_name']}", True, kc_col if is_unlocked else (80, 80, 80))
            self.screen.blit(kc_surf, (x + 14, y + 248))

            # Bio text snippet
            bio = meta['survivor_bio']
            b_surf1 = self.font_small.render(bio[:32], True, (140, 145, 155))
            b_surf2 = self.font_small.render(bio[32:64], True, (140, 145, 155))
            self.screen.blit(b_surf1, (x + 14, y + 278))
            self.screen.blit(b_surf2, (x + 14, y + 296))

        # 3. Bottom Action Buttons
        # Left: Quick Random Map Button
        quick_btn = pg.Rect(70, HEIGHT - 110, 260, 55)
        pg.draw.rect(self.screen, (60, 30, 90), quick_btn, border_radius=10)
        pg.draw.rect(self.screen, COLOR_PURPLE, quick_btn, width=2, border_radius=10)
        q_text = self.font_title.render("⚡ RANDOM MAP", True, COLOR_WHITE)
        self.screen.blit(q_text, q_text.get_rect(center=quick_btn.center))

        # Center: Main DEPLOY MISSION button
        deploy_rect = pg.Rect(WIDTH // 2 - 170, HEIGHT - 110, 340, 55)
        dep_bg = (180, 30, 80) if self.random_map_mode else (220, 40, 50)
        pg.draw.rect(self.screen, dep_bg, deploy_rect, border_radius=10)
        pg.draw.rect(self.screen, (255, 90, 100), deploy_rect, width=2, border_radius=10)

        mode_str = "PROCEDURAL" if self.random_map_mode else "CAMPAIGN"
        dep_text = self.font_title.render(f"DEPLOY LVL {self.selected_level_id} ({mode_str})", True, COLOR_WHITE)
        self.screen.blit(dep_text, dep_text.get_rect(center=deploy_rect.center))

        # Right: Toggle Map Mode Button
        toggle_btn = pg.Rect(WIDTH - 330, HEIGHT - 110, 260, 55)
        pg.draw.rect(self.screen, (25, 35, 45), toggle_btn, border_radius=10)
        pg.draw.rect(self.screen, COLOR_CYAN, toggle_btn, width=2, border_radius=10)
        t_text = self.font_title.render("TOGGLE MODE [R]", True, COLOR_CYAN)
        self.screen.blit(t_text, t_text.get_rect(center=toggle_btn.center))

    def draw_loadout_tab(self):
        header = self.font_title.render("SELECT OPERATIVE COMBAT LOADOUT", True, COLOR_CYAN)
        self.screen.blit(header, (80, 110))

        # 1. Primary Weapons
        w_options = [
            ("shotgun", "Combat 12G Shotgun", "Lethal 2-shell close blast (Short Range, High Dmg), obliterates close infected.", (255, 200, 40)),
            ("rifle", "M4A1 Assault Rifle", "3-round high-velocity burst (Long Range, Med Dmg) for precision swarm defense.", (0, 210, 255)),
            ("pistol", "Tactical 9mm Pistol", "Agile sidearm (Medium Range, Low Dmg) with generous ammo reserves.", (220, 220, 230))
        ]
        for i, (w_key, w_name, w_desc, w_col) in enumerate(w_options):
            r = pg.Rect(80 + i * 360, 160, 320, 170)
            is_sel = (self.selected_primary == w_key)
            bg = (30, 35, 48, 230) if is_sel else (18, 20, 26, 210)
            pg.draw.rect(self.screen, bg, r, border_radius=8)
            pg.draw.rect(self.screen, w_col if is_sel else (50, 55, 65), r, width=3 if is_sel else 1, border_radius=8)

            tag = self.font_bold.render("[EQUIPPED]" if is_sel else "SELECT", True, COLOR_GREEN if is_sel else (140, 145, 155))
            self.screen.blit(tag, (r.x + 16, r.y + 14))

            w_title = self.font_title.render(w_name, True, COLOR_WHITE)
            self.screen.blit(w_title, (r.x + 16, r.y + 38))

            cfg = WEAPON_CONFIGS[w_key]
            stats = f"Dmg: {cfg.get('damage_label', cfg['damage'])} | Range: {cfg.get('range_label', 'Med')} | Clip: {cfg['max_ammo']}"
            st_surf = self.font_small.render(stats, True, COLOR_AMBER)
            self.screen.blit(st_surf, (r.x + 16, r.y + 70))

            # Desc wrapping
            desc_surf = self.font_small.render(w_desc[:44], True, (170, 175, 185))
            self.screen.blit(desc_surf, (r.x + 16, r.y + 100))
            desc_surf2 = self.font_small.render(w_desc[44:], True, (170, 175, 185))
            self.screen.blit(desc_surf2, (r.x + 16, r.y + 120))

        # 2. Tactical Equipment
        t_header = self.font_title.render("SELECT TACTICAL CONSUMABLE", True, COLOR_AMBER)
        self.screen.blit(t_header, (80, 360))

        t_options = [
            ("medkit", "Trauma Medkit (x2)", "Instantly restores 50 Hit Points during combat.", COLOR_GREEN),
            ("grenade", "M67 Frag Grenade (x2)", "Explosive raycast AoE blast damaging adjacent maze tiles.", (240, 110, 30)),
            ("stim", "Adrenaline Stim (x2)", "+45% sprint speed & stamina boost for 10 seconds.", COLOR_CYAN),
        ]
        for i, (t_key, t_name, t_desc, t_col) in enumerate(t_options):
            r = pg.Rect(80 + i * 360, 400, 320, 150)
            is_sel = (self.selected_tactical == t_key)
            bg = (30, 35, 48, 230) if is_sel else (18, 20, 26, 210)
            pg.draw.rect(self.screen, bg, r, border_radius=8)
            pg.draw.rect(self.screen, t_col if is_sel else (50, 55, 65), r, width=3 if is_sel else 1, border_radius=8)

            tag = self.font_bold.render("[EQUIPPED]" if is_sel else "SELECT", True, COLOR_GREEN if is_sel else (140, 145, 155))
            self.screen.blit(tag, (r.x + 16, r.y + 14))

            t_title = self.font_title.render(t_name, True, COLOR_WHITE)
            self.screen.blit(t_title, (r.x + 16, r.y + 38))

            desc_surf = self.font_small.render(t_desc[:44], True, (170, 175, 185))
            self.screen.blit(desc_surf, (r.x + 16, r.y + 75))
            desc_surf2 = self.font_small.render(t_desc[44:], True, (170, 175, 185))
            self.screen.blit(desc_surf2, (r.x + 16, r.y + 95))

        # Passive armor reminder
        armor_box = pg.Rect(80, 580, 1040, 55)
        pg.draw.rect(self.screen, (20, 28, 38), armor_box, border_radius=8)
        pg.draw.rect(self.screen, (0, 210, 255), armor_box, width=1, border_radius=8)
        arm_text = self.font_body.render("PASSIVE GEAR: Tactical Kevlar Armor Vest equipped (Absorbs 40% incoming damage from infected).", True, COLOR_CYAN)
        self.screen.blit(arm_text, (100, 595))

    def draw_profile_tab(self):
        c = self.game.firebase_service.cache
        header = self.font_title.render("OPERATIVE DOSSIER & RESCUE BADGES", True, COLOR_CYAN)
        self.screen.blit(header, (80, 105))

        # Profile Box
        p_box = pg.Rect(80, 145, 480, 480)
        pg.draw.rect(self.screen, (20, 24, 32), p_box, border_radius=10)
        pg.draw.rect(self.screen, (50, 60, 75), p_box, width=2, border_radius=10)

        # Operative info
        callsign = self.font_title.render(f"Callsign: {c.get('username', 'Vance')}", True, COLOR_WHITE)
        self.screen.blit(callsign, (110, 175))

        uid_str = f"Operative ID: {c.get('user_id', 'Unknown')[:18]}..."
        uid_surf = self.font_small.render(uid_str, True, (140, 150, 165))
        self.screen.blit(uid_surf, (110, 210))

        # Stats metrics
        stats = c.get("stats", {})
        kills = stats.get("total_kills", 0)
        rescues = stats.get("survivors_rescued", 0)
        missions = stats.get("missions_completed", 0)
        currency = c.get("currency", 500)

        items = [
            ("Quarantine Sector Clearance", f"{len(c.get('unlocked_levels', [1]))} / 8 Levels"),
            ("Total Infected Eliminated", f"{kills} Zombies"),
            ("VIP Survivors Extracted", f"{rescues} / 8 Rescued"),
            ("Successful Extraction Missions", f"{missions} Missions"),
            ("Hazard Pay Credits", f"{currency} Credits"),
            ("Authentication Status", "Firebase Anonymous Token" if c.get("is_anonymous") else "Firebase Cloud Verified"),
        ]

        for i, (k, v) in enumerate(items):
            ky = 250 + i * 46
            k_surf = self.font_body.render(k, True, (170, 180, 195))
            v_surf = self.font_bold.render(v, True, COLOR_AMBER if "Credit" in k else COLOR_GREEN if "Extracted" in k else COLOR_WHITE)
            self.screen.blit(k_surf, (110, ky))
            self.screen.blit(v_surf, (110, ky + 20))

        # Badges Box (Right Side)
        b_box = pg.Rect(590, 145, 600, 480)
        pg.draw.rect(self.screen, (20, 24, 32), b_box, border_radius=10)
        pg.draw.rect(self.screen, (50, 60, 75), b_box, width=2, border_radius=10)

        b_title = self.font_title.render("CAMPAIGN EXTRACTION HONORS", True, COLOR_AMBER)
        self.screen.blit(b_title, (620, 160))

        badges = [
            (1, "CADUCEUS BADGE", "Dr. Sarah Chen (Field Doctor)", "Extracted medical triage personnel."),
            (2, "CIRCUIT BREAKER", "Marcus Vance (Electrical Engineer)", "Secured metro power grid telemetry."),
            (3, "PATHFINDER STAR", "Jethalal Gada (Gada Electronics)", "Rescued Gokuldham's beloved Jethalal from barricades."),
            (4, "ANTIDOTE HARVESTER", "Dr. Elena Rostova (Virologist)", "Protected mutated pathogen samples."),
            (5, "APOCALYPSE SAVIOR", "Dr. Arthur Sterling (Head Scientist)", "Extracted master vaccine dispersal data."),
            (6, "FLORA SHIELD", "Papu (VIP Survivor Specialist)", "Secured botanical cellular inhibitor."),
            (7, "DEMOLITION CLEAVER", "Chief Alvarez (Demolitions Expert)", "Armed detonator to seal hive caverns."),
            (8, "TOTAL AIRLIFT MEDAL", "Major Katherine Ross (Air Commander)", "Cleared runway for extraction transports."),
        ]

        unlocked_levels = c.get("unlocked_levels", [1])
        for i, (lvl_id, b_name, b_vip, b_desc) in enumerate(badges):
            is_awarded = (lvl_id + 1 in unlocked_levels)
            by = 195 + i * 52

            bg_col = (30, 42, 35) if is_awarded else (18, 20, 24)
            b_border = COLOR_GREEN if is_awarded else (45, 50, 60)
            pg.draw.rect(self.screen, bg_col, (615, by, 550, 48), border_radius=6)
            pg.draw.rect(self.screen, b_border, (615, by, 550, 48), width=2 if is_awarded else 1, border_radius=6)

            badge_col = (255, 215, 30) if is_awarded else (100, 105, 115)
            badge_surf = self.font_bold.render(f"★ {b_name}" if is_awarded else f"🔒 {b_name}", True, badge_col)
            self.screen.blit(badge_surf, (628, by + 6))

            vip_surf = self.font_small.render(f"{b_vip} - {b_desc}", True, COLOR_WHITE if is_awarded else (110, 115, 120))
            self.screen.blit(vip_surf, (628, by + 26))

    def draw_leaderboard_tab(self):
        header = self.font_title.render("GLOBAL QUARANTINE EXTRACTION LEADERBOARD", True, COLOR_CYAN)
        self.screen.blit(header, (80, 95))

        # Filter Level Buttons (1 to 8)
        for lvl_id in range(1, 9):
            bx = 120 + (lvl_id - 1) * 135
            is_active = (self.leaderboard_level == lvl_id)
            r = pg.Rect(bx - 55, 130, 120, 34)
            pg.draw.rect(self.screen, (0, 210, 255, 50) if is_active else (25, 28, 35), r, border_radius=6)
            pg.draw.rect(self.screen, COLOR_CYAN if is_active else (55, 60, 70), r, width=2 if is_active else 1, border_radius=6)

            text = self.font_bold.render(f"LEVEL {lvl_id}", True, COLOR_CYAN if is_active else (150, 160, 170))
            self.screen.blit(text, text.get_rect(center=r.center))

        # Table Header
        tbl_y = 195
        pg.draw.rect(self.screen, (20, 24, 32), (80, tbl_y, 1120, 420), border_radius=8)
        pg.draw.rect(self.screen, (50, 60, 75), (80, tbl_y, 1120, 420), width=2, border_radius=8)

        # Columns
        col_rank = self.font_bold.render("RANK", True, COLOR_AMBER)
        col_user = self.font_bold.render("OPERATIVE CALLSIGN", True, COLOR_AMBER)
        col_time = self.font_bold.render("CLEARANCE TIME", True, COLOR_AMBER)
        col_kills = self.font_bold.render("INFECTED KILLED", True, COLOR_AMBER)

        self.screen.blit(col_rank, (120, tbl_y + 14))
        self.screen.blit(col_user, (260, tbl_y + 14))
        self.screen.blit(col_time, (680, tbl_y + 14))
        self.screen.blit(col_kills, (940, tbl_y + 14))
        pg.draw.line(self.screen, (50, 60, 75), (80, tbl_y + 44), (1200, tbl_y + 44), 2)

        # Fetch records from Supabase service
        records = self.game.supabase_service.get_leaderboard(self.leaderboard_level)
        for i, rec in enumerate(records[:8]):
            ry = tbl_y + 55 + i * 42
            rank_str = f"#{i + 1}"
            rank_col = (255, 215, 30) if i == 0 else (210, 215, 220) if i == 1 else (205, 127, 50) if i == 2 else COLOR_WHITE

            r_surf = self.font_bold.render(rank_str, True, rank_col)
            u_surf = self.font_body.render(rec.get("username", "Unknown"), True, COLOR_WHITE)
            t_surf = self.font_bold.render(f"{rec.get('clear_time_seconds', 0.0)}s", True, COLOR_GREEN)
            k_surf = self.font_body.render(f"{rec.get('zombies_killed', 0)} Kills", True, COLOR_AMBER)

            self.screen.blit(r_surf, (130, ry))
            self.screen.blit(u_surf, (260, ry))
            self.screen.blit(t_surf, (710, ry))
            self.screen.blit(k_surf, (970, ry))

    def draw_settings_tab(self):
        header = self.font_title.render("GAME ENGINE & BACKEND SETTINGS", True, COLOR_CYAN)
        self.screen.blit(header, (80, 110))

        s_box = pg.Rect(80, 160, 1120, 460)
        pg.draw.rect(self.screen, (20, 24, 32), s_box, border_radius=10)
        pg.draw.rect(self.screen, (50, 60, 75), s_box, width=2, border_radius=10)

        settings_list = [
            ("Display Resolution", "1280 x 720 (16:9 Landscape High Performance Mobile Raycaster)"),
            ("Target Framerate", "60 FPS VSync Cap"),
            ("Touch Controls Mode", "Virtual Left Joystick + Right Touch-Look Panning + 6 Action Buttons"),
            ("Sound System", "Pygame Mixer 44.1kHz Stereo with 8-bit Procedural Sound Synthesis"),
            ("Supabase REST API", f"Connected: {self.game.supabase_service.supabase_url or 'Offline Local Fallback Active'}"),
            ("Firebase Authentication", f"Connected: {self.game.firebase_service.current_user.get('display_name', 'Anonymous Active')}"),
            ("Android APK Target", "Python-for-Android / Pygame-CE via buildozer.spec"),
        ]

        for i, (k, v) in enumerate(settings_list):
            sy = 190 + i * 56
            k_surf = self.font_bold.render(k, True, COLOR_AMBER)
            v_surf = self.font_body.render(v, True, COLOR_WHITE)
            self.screen.blit(k_surf, (110, sy))
            self.screen.blit(v_surf, (110, sy + 22))
