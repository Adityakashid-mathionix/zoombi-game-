"""
Main Application Entrypoint: Zombie Quarantine FPS Mobile Engine.
Raycaster architecture with Mobile Touch Controls, 5 Campaign Levels,
Firebase Auth/Sync, and Supabase Leaderboards.
"""
import sys
import pygame as pg

from engine.settings import RES, WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, FPS
from engine.sound_engine import SoundManager
from engine.asset_manager import AssetManager
from engine.map_engine import LevelMap
from engine.player import Player
from engine.weapons import WeaponManager
from engine.pathfinding import PathFinding
from engine.npcs import SpriteManager
from engine.raycasting import RayCasting
from engine.object_renderer import ObjectRenderer
from engine.touch_controls import TouchControlsManager
from backend.supabase_service import SupabaseService
from backend.firebase_service import FirebaseService
from ui.hud import InGameHUD
from ui.lobby_menu import LobbyMenu
from ui.dialogs import DebriefingModal, GameOverModal


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Zombi Apploclips")
        flags = pg.SCALED if hasattr(pg, "SCALED") else 0
        self.screen = pg.display.set_mode(RES, flags)
        self.clock = pg.time.Clock()
        self.delta_time = 1.0
        self.elapsed_time = 0.0
        self.state = "LOBBY"  # LOBBY, GAMEPLAY, VICTORY, GAME_OVER
        self.mouse_look_enabled = False
        self.is_suspended = False

        # Initialize Backend Services
        self.supabase_service = SupabaseService()
        self.firebase_service = FirebaseService()

        # Initialize Sound & Assets
        self.sound_manager = SoundManager()
        self.asset_manager = AssetManager()

        # UI Menus & Modals
        self.lobby_menu = LobbyMenu(self)
        self.debriefing_modal = DebriefingModal(self)
        self.game_over_modal = GameOverModal(self)

        # Gameplay Components (initialized on mission deploy)
        self.level_map = None
        self.player = None
        self.weapon_manager = None
        self.pathfinding = None
        self.sprite_manager = None
        self.raycasting = None
        self.object_renderer = None
        self.hud = None
        self.touch_controls = None

    def start_mission(self, level_id=1, primary_weapon=None, tactical_item=None, random_map=False):
        """Initializes raycaster world and deploys mission."""
        self.level_map = LevelMap(level_id, random_map=random_map)
        self.player = Player(self)
        self.weapon_manager = WeaponManager(self)
        self.pathfinding = PathFinding(self)
        self.sprite_manager = SpriteManager(self)
        self.raycasting = RayCasting(self)
        self.object_renderer = ObjectRenderer(self)
        self.hud = InGameHUD(self)
        self.touch_controls = TouchControlsManager(self)

        # Apply equipped loadout
        prim = primary_weapon or self.firebase_service.cache["loadout"]["primary_weapon"]
        tact = tactical_item or self.firebase_service.cache["loadout"]["tactical_item"]
        self.weapon_manager.select_weapon(prim)

        if tact == "grenade":
            self.weapon_manager.inventory["grenade"] += 2
        elif tact == "medkit":
            self.weapon_manager.inventory["medkit"] += 2
        elif tact in ("stim", "adrenaline"):
            self.weapon_manager.inventory["stim"] += 2
        elif tact == "armor_vest":
            self.player.armor = 100

        self.elapsed_time = 0.0
        self.state = "GAMEPLAY"
        self.mouse_look_enabled = True
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        pg.mouse.get_rel()  # flush residual delta

    def trigger_level_victory(self):
        """Called upon reaching extraction with survivor rescued."""
        self.state = "VICTORY"
        self.mouse_look_enabled = False
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        self.debriefing_modal.reset()
        lvl_id = self.level_map.level_id
        meta = self.level_map.meta
        user_id = self.firebase_service.cache["user_id"]
        username = self.firebase_service.cache["username"]

        # 1. Submit score to Supabase Leaderboards
        self.supabase_service.submit_score(
            user_id, username, lvl_id, self.elapsed_time, self.player.kills
        )

        # 2. Award rescue badge
        self.supabase_service.award_survivor_badge(user_id, lvl_id, meta["survivor"])

        # 3. Unlock progression in Firebase
        self.firebase_service.unlock_next_level(lvl_id)

    def trigger_game_over(self):
        self.state = "GAME_OVER"
        self.mouse_look_enabled = False
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        self.game_over_modal.reset()

    def return_to_lobby(self):
        self.state = "LOBBY"
        self.mouse_look_enabled = False
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        pg.display.set_caption("Zombi Apploclips")

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Android lifecycle suspend / resume handling
            if event.type in (
                getattr(pg, "APP_WILLENTERBACKGROUND", -101),
                getattr(pg, "APP_DIDENTERBACKGROUND", -102),
                getattr(pg, "WINDOWMINIMIZED", -103)
            ):
                self.is_suspended = True
                try:
                    pg.mixer.pause()
                    pg.mixer.music.pause()
                except Exception:
                    pass
                continue

            if event.type in (
                getattr(pg, "APP_WILLENTERFOREGROUND", -104),
                getattr(pg, "APP_DIDENTERFOREGROUND", -105),
                getattr(pg, "WINDOWRESTORED", -106)
            ):
                self.is_suspended = False
                try:
                    pg.mixer.unpause()
                    pg.mixer.music.unpause()
                except Exception:
                    pass
                self.clock.tick(FPS)
                continue

            # Global ESC & Android Back button logic
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, getattr(pg, "K_AC_BACK", -107)):
                    if self.state == "GAMEPLAY":
                        self.return_to_lobby()
                    elif self.state in ("VICTORY", "GAME_OVER"):
                        self.return_to_lobby()
                    else:
                        pg.quit()
                        sys.exit()

                # Toggle desktop mouse look with M key or Tab
                if event.key in (pg.K_m, pg.K_TAB) and self.state == "GAMEPLAY":
                    self.mouse_look_enabled = not self.mouse_look_enabled
                    pg.mouse.set_visible(not self.mouse_look_enabled)
                    pg.event.set_grab(self.mouse_look_enabled)
                    if self.mouse_look_enabled:
                        pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
                        pg.mouse.get_rel()  # flush residual delta

                # Quick desktop weapon shortcuts
                if self.state == "GAMEPLAY":
                    if event.key == pg.K_1:
                        self.weapon_manager.select_weapon("pistol")
                    elif event.key == pg.K_2:
                        self.weapon_manager.select_weapon("shotgun")
                    elif event.key == pg.K_3:
                        self.weapon_manager.select_weapon("rifle")
                    elif event.key == pg.K_r:
                        self.weapon_manager.start_reload()
                    elif event.key == pg.K_e:
                        self.player.interact()
                    elif event.key == pg.K_g:
                        self.weapon_manager.throw_grenade()
                    elif event.key == pg.K_h:
                        self.weapon_manager.use_medkit()
                    elif event.key == pg.K_q:
                        self.weapon_manager.use_adrenaline()
                    elif event.key == pg.K_SPACE:
                        self.weapon_manager.shoot()

                # Modal keyboard progression
                elif self.state == "VICTORY":
                    if event.key in (pg.K_RETURN, pg.K_SPACE):
                        self.debriefing_modal.handle_click((WIDTH - 700) // 2 + 100, (HEIGHT - 520) // 2 + 520 - 50)
                elif self.state == "GAME_OVER":
                    if event.key in (pg.K_RETURN, pg.K_SPACE, pg.K_r):
                        self.game_over_modal.handle_click(WIDTH // 2 - 120, HEIGHT // 2 + 65)

            # Mouse click in gameplay: re-captures mouse or fires weapon
            if event.type == pg.MOUSEBUTTONDOWN and self.state == "GAMEPLAY":
                if not self.mouse_look_enabled:
                    self.mouse_look_enabled = True
                    pg.mouse.set_visible(False)
                    pg.event.set_grab(True)
                    pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
                    pg.mouse.get_rel()
                elif event.button == 1:
                    self.weapon_manager.shoot()

            # State-specific event handling
            if self.state == "LOBBY":
                self.lobby_menu.handle_event(event)
            elif self.state == "GAMEPLAY":
                self.touch_controls.handle_event(event)
            elif self.state == "VICTORY":
                if event.type in (pg.MOUSEBUTTONDOWN, pg.FINGERDOWN):
                    mx, my = event.pos if hasattr(event, "pos") else (int(event.x * WIDTH), int(event.y * HEIGHT))
                    self.debriefing_modal.handle_click(mx, my)
            elif self.state == "GAME_OVER":
                if event.type in (pg.MOUSEBUTTONDOWN, pg.FINGERDOWN):
                    mx, my = event.pos if hasattr(event, "pos") else (int(event.x * WIDTH), int(event.y * HEIGHT))
                    self.game_over_modal.handle_click(mx, my)

    def update(self):
        if self.is_suspended:
            return

        dt = self.delta_time

        if self.state == "GAMEPLAY":
            self.elapsed_time += dt / 1000.0

            # Gather touch controls input
            self.touch_controls.update()
            joy_x, joy_y = self.touch_controls.get_movement_input()
            look_delta = self.touch_controls.get_and_reset_look_delta()

            # Update Player
            self.player.update_movement(dt, joy_x, joy_y, look_delta)

            # Update Weapon Manager
            self.weapon_manager.update(dt)

            # Continuous burst fire handling for Assault Rifle while fire input is held
            if self.weapon_manager.current_weapon_key == "rifle":
                mouse_firing = self.mouse_look_enabled and pg.mouse.get_pressed()[0]
                key_firing = pg.key.get_pressed()[pg.K_SPACE]
                touch_firing = self.touch_controls.is_shoot_held()
                if mouse_firing or key_firing or touch_firing:
                    self.weapon_manager.shoot()

            # Update Sprites and Entities
            self.sprite_manager.update(dt)

            # Raycasting scene calculations
            self.raycasting.update()

            # HUD timers and notices
            self.hud.update(dt)

        elif self.state == "VICTORY":
            self.debriefing_modal.update(dt)

        elif self.state == "GAME_OVER":
            self.game_over_modal.update(dt)

    def draw(self):
        if self.state == "LOBBY":
            self.lobby_menu.draw()

        elif self.state in ("GAMEPLAY", "VICTORY", "GAME_OVER"):
            # 1. 3D Raycasting Scene Compositing
            self.object_renderer.draw()

            # 2. Weapon Viewmodel
            self.weapon_manager.draw_viewmodel(self.screen)

            # 3. In-Game Mobile HUD
            self.hud.draw(self.screen)

            # 4. On-Screen Touch Controls (Virtual Joystick & Action Buttons)
            if self.state == "GAMEPLAY":
                self.touch_controls.draw(self.screen)

            # 5. Victory or Game Over Modals
            if self.state == "VICTORY":
                self.debriefing_modal.draw(self.screen)
            elif self.state == "GAME_OVER":
                self.game_over_modal.draw(self.screen)

        pg.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            raw_dt = self.clock.tick(FPS)
            self.delta_time = min(50.0, max(1.0, float(raw_dt)))
            if self.state == "GAMEPLAY":
                pg.display.set_caption(f"Zombi Apploclips - FPS: {self.clock.get_fps():.1f}")


if __name__ == "__main__":
    game = Game()
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("--play", "-p", "play", "1", "level1", "--level1"):
            game.start_mission(1)
        elif arg in ("2", "level2"):
            game.start_mission(2)
        elif arg in ("3", "level3"):
            game.start_mission(3)
        elif arg in ("4", "level4"):
            game.start_mission(4)
        elif arg in ("5", "level5"):
            game.start_mission(5)
        elif arg in ("6", "level6"):
            game.start_mission(6)
        elif arg in ("7", "level7"):
            game.start_mission(7)
        elif arg in ("8", "level8"):
            game.start_mission(8)
    game.run()
