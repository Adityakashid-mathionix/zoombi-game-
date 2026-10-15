"""
Player Controller: First-person physics, health, armor absorption,
keyboard/mouse & virtual touch joystick movement, interactions, and objectives.
"""
import math
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, PLAYER_POS, PLAYER_ANGLE, PLAYER_SPEED, PLAYER_RUN_SPEED,
    PLAYER_ROT_SPEED, PLAYER_SIZE_SCALE, PLAYER_MAX_HEALTH, PLAYER_MAX_ARMOR,
    MOUSE_SENSITIVITY, MOUSE_MAX_REL, MOUSE_BORDER_LEFT, MOUSE_BORDER_RIGHT,
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
        self.is_running = False
        self.is_dead = False
        self.diag_move_corr = 1 / math.sqrt(2)

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
        """Exact Reference DOOM wall sliding physics: tests independent X and Y movement axes."""
        dt = max(1.0, self.game.delta_time)
        scale = PLAYER_SIZE_SCALE / dt
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def mouse_control(self):
        """Exact Reference DOOM smooth mouse look controller."""
        if not self.game.mouse_look_enabled:
            return 0.0
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        return self.rel * MOUSE_SENSITIVITY * max(1.0, self.game.delta_time)

    def update_movement(self, dt, touch_move_x=0.0, touch_move_y=0.0, touch_look=0.0):
        keys = pg.key.get_pressed()
        self.is_running = bool(keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT])

        # Base speed selection: walk vs sprint
        speed_rate = PLAYER_RUN_SPEED if self.is_running else PLAYER_SPEED
        if self.adrenaline_active:
            speed_rate *= 1.45

        base_speed = speed_rate * dt
        dx, dy = 0.0, 0.0
        self.is_moving = False

        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        # 1. Desktop Keyboard Movement (Reference DOOM logic with diagonal correction)
        kb_dx, kb_dy = 0.0, 0.0
        num_key_pressed = -1
        speed_sin = base_speed * sin_a
        speed_cos = base_speed * cos_a

        if keys[pg.K_w] or keys[pg.K_UP]:
            num_key_pressed += 1
            kb_dx += speed_cos
            kb_dy += speed_sin
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            num_key_pressed += 1
            kb_dx -= speed_cos
            kb_dy -= speed_sin
        if keys[pg.K_a]:
            num_key_pressed += 1
            kb_dx += speed_sin
            kb_dy -= speed_cos
        if keys[pg.K_d]:
            num_key_pressed += 1
            kb_dx -= speed_sin
            kb_dy += speed_cos

        if num_key_pressed >= 0:
            self.is_moving = True
            if num_key_pressed > 0:
                kb_dx *= self.diag_move_corr
                kb_dy *= self.diag_move_corr
            dx += kb_dx
            dy += kb_dy

        # 2. Touch Virtual Joystick Input
        joy_len = math.hypot(touch_move_x, touch_move_y)
        if joy_len > 0.05:
            self.is_moving = True
            # Outer rim auto-run
            if joy_len > 0.70:
                self.is_running = True
                joy_speed = (PLAYER_RUN_SPEED * (1.45 if self.adrenaline_active else 1.0)) * dt
            else:
                joy_speed = base_speed

            norm_x = touch_move_x / joy_len if joy_len > 1.0 else touch_move_x
            norm_y = touch_move_y / joy_len if joy_len > 1.0 else touch_move_y

            fwd = -norm_y * joy_speed
            strafe = norm_x * joy_speed

            joy_dx = fwd * cos_a - strafe * sin_a
            joy_dy = fwd * sin_a + strafe * cos_a
            dx += joy_dx
            dy += joy_dy

        # Apply smooth independent-axis sliding collision
        self.check_wall_collision(dx, dy)

        # Smooth Rotation from Touch, Keyboard, or Mouse
        rot_delta = self.mouse_control()
        if touch_look != 0.0:
            rot_delta += touch_look * TOUCH_LOOK_SENSITIVITY
        if keys[pg.K_LEFT]:
            rot_delta -= PLAYER_ROT_SPEED * dt
        if keys[pg.K_RIGHT]:
            rot_delta += PLAYER_ROT_SPEED * dt

        self.rel = rot_delta
        self.angle = (self.angle + rot_delta) % math.tau

        # Weapon bobbing
        if self.is_moving:
            self.bob_timer += dt * (1.5 if self.is_running else 1.0)

        # Adrenaline timer
        if self.adrenaline_active:
            self.adrenaline_timer -= dt
            if self.adrenaline_timer <= 0:
                self.adrenaline_active = False

        self.check_interactions()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
