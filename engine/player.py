"""
Player Controller: First-person physics, health, armor absorption,
keyboard/mouse & virtual touch joystick movement, interactions, and objectives.
"""
import math
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, PLAYER_POS, PLAYER_ANGLE, PLAYER_SPEED, PLAYER_ROT_SPEED,
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

    def check_wall(self, x, y):
        """Returns True if world position (x, y) is passable and not a wall or closed door."""
        return not self.game.level_map.is_wall(x, y)

    def check_wall_collision(self, dx, dy):
        """Authentic DOOM wall sliding physics: tests X and Y movement axes independently."""
        radius = 0.22  # Player collision radius in world grid units

        # Test and apply X movement
        if dx != 0.0:
            check_x = self.x + dx + (radius if dx > 0 else -radius)
            if self.check_wall(check_x, self.y):
                self.x += dx

        # Test and apply Y movement
        if dy != 0.0:
            check_y = self.y + dy + (radius if dy > 0 else -radius)
            if self.check_wall(self.x, check_y):
                self.y += dy

    def update_movement(self, dt, touch_move_x=0.0, touch_move_y=0.0, touch_look=0.0):
        # Calculate speed with adrenaline multiplier
        base_speed = PLAYER_SPEED * (1.45 if self.adrenaline_active else 1.0) * dt
        dx, dy = 0.0, 0.0
        self.is_moving = False

        # Touch Virtual Joystick Input
        if abs(touch_move_x) > 0.05 or abs(touch_move_y) > 0.05:
            self.is_moving = True
            sin_a = math.sin(self.angle)
            cos_a = math.cos(self.angle)

            fwd = -touch_move_y * base_speed
            strafe = touch_move_x * base_speed

            joy_dx = fwd * cos_a - strafe * sin_a
            joy_dy = fwd * sin_a + strafe * cos_a

            # Diagonal normalization for joystick
            joy_len = math.hypot(touch_move_x, touch_move_y)
            if joy_len > 1.0:
                joy_dx /= joy_len
                joy_dy /= joy_len

            dx += joy_dx
            dy += joy_dy

        # Desktop Keyboard Movement
        keys = pg.key.get_pressed()
        kb_dx, kb_dy = 0.0, 0.0
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        fwd_move = 0
        side_move = 0
        if keys[pg.K_w] or keys[pg.K_UP]:
            fwd_move += 1
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            fwd_move -= 1
        if keys[pg.K_a]:
            side_move -= 1
        if keys[pg.K_d]:
            side_move += 1

        if fwd_move != 0 or side_move != 0:
            self.is_moving = True
            move_scale = base_speed
            # Normalize diagonal speed (W+A, W+D, S+A, S+D)
            if fwd_move != 0 and side_move != 0:
                move_scale *= (1.0 / math.sqrt(2.0))

            kb_dx += (fwd_move * cos_a - side_move * sin_a) * move_scale
            kb_dy += (fwd_move * sin_a + side_move * cos_a) * move_scale
            dx += kb_dx
            dy += kb_dy

        # Apply smooth independent-axis sliding collision
        self.check_wall_collision(dx, dy)

        # Smooth Rotation from Touch, Keyboard, or Mouse
        rot_delta = 0.0
        if touch_look != 0.0:
            rot_delta += touch_look * TOUCH_LOOK_SENSITIVITY
        if keys[pg.K_LEFT]:
            rot_delta -= PLAYER_ROT_SPEED * dt
        if keys[pg.K_RIGHT]:
            rot_delta += PLAYER_ROT_SPEED * dt

        # Smooth Desktop Mouse Look
        if self.game.mouse_look_enabled:
            mx, my = pg.mouse.get_pos()
            if mx < 80 or mx > WIDTH - 80 or my < 80 or my > HEIGHT - 80:
                pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
                pg.mouse.get_rel()  # flush center jump
            else:
                m_rel = pg.mouse.get_rel()[0]
                m_rel = max(-35, min(35, m_rel))
                rot_delta += m_rel * 0.0018

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
