"""
Player Controller: First-person physics, health, armor absorption,
keyboard/mouse & virtual touch joystick movement, interactions, and objectives.
"""
import math
import pygame as pg
from engine.settings import (
    PLAYER_POS, PLAYER_ANGLE, PLAYER_SPEED, PLAYER_ROT_SPEED,
    PLAYER_MAX_HEALTH, PLAYER_MAX_ARMOR, MOUSE_SENSITIVITY,
    TOUCH_LOOK_SENSITIVITY, HALF_WIDTH, HALF_HEIGHT
)


class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = self.game.level_map.player_start
        self.angle = 0.0
        self.health = PLAYER_MAX_HEALTH
        self.armor = 100  # Starts with standard Kevlar vest
        self.kills = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.rel = 0.0
        self.bob_timer = 0
        self.is_moving = False
        self.is_dead = False

        # Adrenaline boost state
        self.adrenaline_active = False
        self.adrenaline_timer = 0

        # Interaction contextual pointers
        self.near_survivor = None
        self.near_door = None
        self.near_extraction = False

    def apply_adrenaline(self):
        self.adrenaline_active = True
        self.adrenaline_timer = 10000  # 10 seconds

    def take_damage(self, damage):
        if self.is_dead:
            return

        # Armor absorbs 40% of damage
        if self.armor > 0:
            absorb = int(damage * 0.40)
            actual_absorb = min(self.armor, absorb)
            self.armor -= actual_absorb
            actual_damage = damage - actual_absorb
        else:
            actual_damage = damage

        self.health -= actual_damage
        self.game.sound_manager.play_player_pain()
        self.game.object_renderer.trigger_damage()

        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        self.is_dead = True
        self.game.sound_manager.play_player_pain()
        self.game.trigger_game_over()

    def check_interactions(self):
        """Check proximity to doors, survivor, or extraction zone."""
        # 1. Check nearby doors
        px, py = int(self.x), int(self.y)
        self.near_door = None
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            check_tile = (px + dx, py + dy)
            if check_tile in self.game.level_map.door_positions:
                door_data = self.game.level_map.door_positions[check_tile]
                if not door_data["open"]:
                    self.near_door = (check_tile, door_data["required_keycard"])
                    break

        # 2. Check nearby extraction zone
        ext_x, ext_y = self.game.level_map.extraction_pos
        dist_ext = math.hypot(self.x - ext_x, self.y - ext_y)
        self.near_extraction = (dist_ext < 1.6)

        # Trigger auto-extraction if player steps on unlocked evacuation pad
        if self.near_extraction and self.game.level_map.extraction_unlocked:
            self.game.trigger_level_victory()

    def interact(self):
        """Contextual interaction: rescue survivor or unlock security door."""
        # Rescue survivor
        if self.near_survivor and not self.near_survivor.rescued:
            self.near_survivor.rescue()
            return True

        # Unlock door
        if self.near_door:
            tile_pos, req_card = self.near_door
            if req_card in self.game.weapon_manager.inventory["keycards"]:
                self.game.level_map.unlock_door(tile_pos)
                self.game.sound_manager.play_door_unlock()
                self.game.hud.show_message("SECURITY ACCESS GRANTED - DOOR UNLOCKED", (40, 220, 80))
                self.near_door = None
                return True
            else:
                self.game.hud.show_message(f"ACCESS DENIED! REQUIRES {req_card.upper()} KEYCARD", (240, 40, 40))
                return False

        # Extraction portal
        if self.near_extraction:
            if self.game.level_map.extraction_unlocked:
                self.game.trigger_level_victory()
                return True
            else:
                self.game.hud.show_message("EXTRACTION LOCKED: RESCUE SURVIVOR FIRST!", (240, 180, 30))
                return False
        return False

    def update_movement(self, dt, touch_move_x=0.0, touch_move_y=0.0, touch_look=0.0):
        # Calculate speed with adrenaline multiplier
        base_speed = PLAYER_SPEED * (1.45 if self.adrenaline_active else 1.0) * dt
        dx, dy = 0.0, 0.0
        self.is_moving = False

        # Touch Virtual Joystick Input
        if abs(touch_move_x) > 0.05 or abs(touch_move_y) > 0.05:
            self.is_moving = True
            # Forward/backward relative to player angle
            sin_a = math.sin(self.angle)
            cos_a = math.cos(self.angle)

            # touch_move_y is forward/backward (-1 is up/forward, 1 is down/backward)
            # touch_move_x is strafe left/right (-1 is left, 1 is right)
            fwd = -touch_move_y * base_speed
            strafe = touch_move_x * base_speed

            dx += fwd * cos_a - strafe * sin_a
            dy += fwd * sin_a + strafe * cos_a

        # Desktop Keyboard Fallback
        keys = pg.key.get_pressed()
        kb_dx, kb_dy = 0.0, 0.0
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        if keys[pg.K_w] or keys[pg.K_UP]:
            kb_dx += cos_a * base_speed
            kb_dy += sin_a * base_speed
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            kb_dx -= cos_a * base_speed
            kb_dy -= sin_a * base_speed
        if keys[pg.K_a]:
            kb_dx += sin_a * base_speed
            kb_dy -= cos_a * base_speed
        if keys[pg.K_d]:
            kb_dx -= sin_a * base_speed
            kb_dy += cos_a * base_speed

        if kb_dx != 0.0 or kb_dy != 0.0:
            self.is_moving = True
            dx += kb_dx
            dy += kb_dy

        # Check collision with walls (sliding physics)
        buffer = 0.28
        check_x = self.x + (buffer if dx > 0 else -buffer)
        check_y = self.y + (buffer if dy > 0 else -buffer)

        if not self.game.level_map.is_wall(check_x + dx, self.y):
            self.x += dx
        if not self.game.level_map.is_wall(self.x, check_y + dy):
            self.y += dy

        # Rotation from Touch Panning or Mouse or Keyboard Arrows
        rot_delta = 0.0
        if touch_look != 0.0:
            rot_delta += touch_look * TOUCH_LOOK_SENSITIVITY
        if keys[pg.K_LEFT]:
            rot_delta -= PLAYER_ROT_SPEED * dt
        if keys[pg.K_RIGHT]:
            rot_delta += PLAYER_ROT_SPEED * dt

        # Desktop mouse relative
        if self.game.mouse_look_enabled:
            mouse_rel = pg.mouse.get_rel()[0]
            rot_delta += mouse_rel * MOUSE_SENSITIVITY

        self.rel = rot_delta
        self.angle = (self.angle + rot_delta) % math.tau

        # Weapon bobbing
        if self.is_moving:
            self.bob_timer += dt

        # Adrenaline timer
        if self.adrenaline_active:
            self.adrenaline_timer -= dt
            if self.adrenaline_timer <= 0:
                self.adrenaline_active = False

        self.check_interactions()

    @property
    def pos(self):
        return self.x, self.y
