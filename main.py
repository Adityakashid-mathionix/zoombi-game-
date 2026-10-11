"""
Main Application Entrypoint: Zombie Quarantine FPS Mobile Engine.
Raycaster architecture with Mobile Touch Controls, 5 Campaign Levels,
Firebase Auth/Sync, and Supabase Leaderboards.
"""
import sys
import pygame as pg

from engine.settings import RES, WIDTH, HEIGHT, FPS
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
        pg.display.set_caption("Zombie Quarantine FPS - Operation Breakout")
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1.0
        self.elapsed_time = 0.0
        self.state = "LOBBY"  # LOBBY, GAMEPLAY, VICTORY, GAME_OVER
        self.mouse_look_enabled = False

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
        elif tact == "stim":
            self.weapon_manager.inventory["stim"] += 2

        self.elapsed_time = 0.0
        self.state = "GAMEPLAY"
        self.mouse_look_enabled = False

    def trigger_level_victory(self):
        """Called upon reaching extraction with survivor rescued."""
        self.state = "VICTORY"
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

    def return_to_lobby(self):
        self.state = "LOBBY"
        self.mouse_look_enabled = False

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Global ESC key logic
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
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

            # Mouse / touch desktop firing
            if event.type == pg.MOUSEBUTTONDOWN and self.state == "GAMEPLAY":
                if event.button == 1 and self.mouse_look_enabled:
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

            # Update Sprites and Entities
            self.sprite_manager.update(dt)

            # Raycasting scene calculations
            self.raycasting.update()

            # HUD timers and notices
            self.hud.update(dt)

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
            self.delta_time = self.clock.tick(FPS)


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
    game.run()
