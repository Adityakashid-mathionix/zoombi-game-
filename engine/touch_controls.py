"""
Mobile Touch Controls Engine:
Virtual Joystick, Touch-Look Panning, Multi-touch tracking, and On-screen Action Buttons.
"""
import math
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, JOYSTICK_RADIUS, JOYSTICK_DEADZONE,
    BUTTON_RADIUS, COLOR_WHITE, COLOR_BLOOD, COLOR_AMBER,
    COLOR_CYAN, COLOR_GREEN, COLOR_PURPLE, safe_font
)


class VirtualJoystick:
    """Virtual analog thumbstick for omnidirectional player movement."""
    def __init__(self, center_pos=(160, HEIGHT - 160), radius=JOYSTICK_RADIUS):
        self.center_x, self.center_y = center_pos
        self.radius = radius
        self.current_x = self.center_x
        self.current_y = self.center_y
        self.active_finger_id = None
        self.move_vector = (0.0, 0.0)  # (x, y) normalized -1.0 to 1.0

    def handle_touch_down(self, x, y, finger_id):
        dist = math.hypot(x - self.center_x, y - self.center_y)
        if dist <= self.radius * 1.5 and self.active_finger_id is None:
            self.active_finger_id = finger_id
            self.update_knob_position(x, y)
            return True
        return False

    def handle_touch_motion(self, x, y, finger_id):
        if self.active_finger_id == finger_id:
            self.update_knob_position(x, y)
            return True
        return False

    def handle_touch_up(self, finger_id):
        if self.active_finger_id == finger_id:
            self.active_finger_id = None
            self.current_x = self.center_x
            self.current_y = self.center_y
            self.move_vector = (0.0, 0.0)
            return True
        return False

    def update_knob_position(self, x, y):
        dx = x - self.center_x
        dy = y - self.center_y
        dist = math.hypot(dx, dy)

        if dist < JOYSTICK_DEADZONE:
            self.current_x = self.center_x
            self.current_y = self.center_y
            self.move_vector = (0.0, 0.0)
            return

        clamped_dist = min(self.radius, dist)
        angle = math.atan2(dy, dx)
        self.current_x = self.center_x + math.cos(angle) * clamped_dist
        self.current_y = self.center_y + math.sin(angle) * clamped_dist

        norm_factor = (clamped_dist - JOYSTICK_DEADZONE) / (self.radius - JOYSTICK_DEADZONE)
        self.move_vector = (math.cos(angle) * norm_factor, math.sin(angle) * norm_factor)

    def draw(self, screen):
        # Outer translucent ring
        base_surf = pg.Surface((self.radius * 2 + 20, self.radius * 2 + 20), pg.SRCALPHA)
        center = (self.radius + 10, self.radius + 10)
        pg.draw.circle(base_surf, (30, 35, 45, 120), center, self.radius)
        pg.draw.circle(base_surf, (0, 210, 255, 160), center, self.radius, 3)
        pg.draw.circle(base_surf, (0, 210, 255, 60), center, JOYSTICK_DEADZONE, 1)

        screen.blit(base_surf, (self.center_x - center[0], self.center_y - center[1]))

        # Inner thumb knob
        knob_r = 30
        knob_surf = pg.Surface((knob_r * 2, knob_r * 2), pg.SRCALPHA)
        knob_center = (knob_r, knob_r)
        pg.draw.circle(knob_surf, (0, 210, 255, 210), knob_center, knob_r)
        pg.draw.circle(knob_surf, (255, 255, 255, 240), knob_center, knob_r - 6)
        screen.blit(knob_surf, (int(self.current_x) - knob_r, int(self.current_y) - knob_r))


class TouchButton:
    """Mobile interactive action button with icons and tap states."""
    def __init__(self, action_id, center_pos, radius, label, color, icon_type="text"):
        self.action_id = action_id
        self.center_x, self.center_y = center_pos
        self.radius = radius
        self.label = label
        self.color = color
        self.icon_type = icon_type
        self.is_pressed = False
        self.active_finger_id = None
        self.highlight = False

    def is_inside(self, x, y):
        return math.hypot(x - self.center_x, y - self.center_y) <= self.radius * 1.15

    def handle_touch_down(self, x, y, finger_id):
        if self.is_inside(x, y) and self.active_finger_id is None:
            self.active_finger_id = finger_id
            self.is_pressed = True
            return True
        return False

    def handle_touch_up(self, finger_id):
        if self.active_finger_id == finger_id:
            self.active_finger_id = None
            self.is_pressed = False
            return True
        return False

    def draw(self, screen, font):
        r = self.radius
        btn_surf = pg.Surface((r * 2 + 10, r * 2 + 10), pg.SRCALPHA)
        c = (r + 5, r + 5)

        # Background circle
        alpha = 230 if self.is_pressed else (190 if self.highlight else 130)
        base_col = (*self.color[:3], alpha)
        pg.draw.circle(btn_surf, (20, 22, 28, 170), c, r)
        pg.draw.circle(btn_surf, base_col, c, r, 0 if self.is_pressed else 3)

        if self.highlight:
            pg.draw.circle(btn_surf, (255, 255, 255, 220), c, r + 2, 2)

        screen.blit(btn_surf, (self.center_x - c[0], self.center_y - c[1]))

        # Render Button Label
        text_surf = font.render(self.label, True, COLOR_WHITE)
        text_rect = text_surf.get_rect(center=(self.center_x, self.center_y))
        screen.blit(text_surf, text_rect)


class TouchControlsManager:
    """Coordinates virtual joystick, right-screen touch-look panning, and action buttons."""

    def __init__(self, game):
        self.game = game
        self.joystick = VirtualJoystick()
        self.font = safe_font(14, bold=True)
        self.large_font = safe_font(18, bold=True)

        # Look drag tracking
        self.look_finger_id = None
        self.last_look_x = 0
        self.look_delta = 0.0
        self.touch_active = False

        # Action Buttons Layout (Right side of mobile landscape screen)
        # 1. SHOOT (Large Red)
        btn_shoot = TouchButton("shoot", (WIDTH - 110, HEIGHT - 160), 46, "FIRE", COLOR_BLOOD)
        # 2. RELOAD (Amber)
        btn_reload = TouchButton("reload", (WIDTH - 210, HEIGHT - 130), 34, "RELOAD", COLOR_AMBER)
        # 3. SWITCH (Cyan)
        btn_switch = TouchButton("switch", (WIDTH - 110, HEIGHT - 275), 34, "SWITCH", COLOR_CYAN)
        # 4. INTERACT / RESCUE (Green)
        btn_interact = TouchButton("interact", (WIDTH - 210, HEIGHT - 225), 38, "ACTION", COLOR_GREEN)
        # 5. GRENADE (Orange)
        btn_grenade = TouchButton("grenade", (WIDTH - 300, HEIGHT - 130), 30, "FRAG", (240, 110, 30))
        # 6. MEDKIT (Teal)
        btn_medkit = TouchButton("medkit", (WIDTH - 300, HEIGHT - 225), 30, "HEAL", (40, 200, 150))

        self.buttons = [btn_shoot, btn_reload, btn_switch, btn_interact, btn_grenade, btn_medkit]

    def update(self):
        # Update contextual highlight for Action button
        interact_btn = next((b for b in self.buttons if b.action_id == "interact"), None)
        if interact_btn:
            interact_btn.highlight = (
                self.game.player.near_survivor is not None or
                self.game.player.near_door is not None or
                self.game.player.near_extraction
            )
            if self.game.player.near_door:
                interact_btn.label = "UNLOCK"
            elif self.game.player.near_survivor:
                interact_btn.label = "RESCUE"
            elif self.game.player.near_extraction:
                interact_btn.label = "EVAC"
            else:
                interact_btn.label = "ACTION"

    def handle_event(self, event):
        """Processes Pygame touch and mouse events."""
        # Multi-touch events (mobile / SDL)
        if event.type == pg.FINGERDOWN:
            self.touch_active = True
            x = event.x * WIDTH
            y = event.y * HEIGHT
            fid = event.finger_id
            self.process_touch_down(x, y, fid)

        elif event.type == pg.FINGERMOTION:
            x = event.x * WIDTH
            y = event.y * HEIGHT
            fid = event.finger_id
            self.process_touch_motion(x, y, fid)

        elif event.type == pg.FINGERUP:
            fid = event.finger_id
            self.process_touch_up(fid)

        # Desktop mouse fallback simulation
        elif event.type == pg.MOUSEBUTTONDOWN:
            mx, my = event.pos
            self.process_touch_down(mx, my, "mouse")

        elif event.type == pg.MOUSEMOTION:
            if pg.mouse.get_pressed()[0]:
                mx, my = event.pos
                self.process_touch_motion(mx, my, "mouse")

        elif event.type == pg.MOUSEBUTTONUP:
            self.process_touch_up("mouse")

    def process_touch_down(self, x, y, fid):
        # 1. Check joystick
        if self.joystick.handle_touch_down(x, y, fid):
            return

        # 2. Check action buttons
        for btn in self.buttons:
            if btn.handle_touch_down(x, y, fid):
                self.trigger_button_action(btn.action_id)
                return

        # 3. Touch-look area on right half of screen (only for touch or when mouse-look is off)
        if x > WIDTH // 2 and self.look_finger_id is None:
            if fid != "mouse" or not self.game.mouse_look_enabled:
                self.look_finger_id = fid
                self.last_look_x = x

    def process_touch_motion(self, x, y, fid):
        if self.joystick.handle_touch_motion(x, y, fid):
            return

        if fid == self.look_finger_id:
            dx = x - self.last_look_x
            self.look_delta += dx
            self.last_look_x = x

    def process_touch_up(self, fid):
        self.joystick.handle_touch_up(fid)
        for btn in self.buttons:
            btn.handle_touch_up(fid)
        if fid == self.look_finger_id:
            self.look_finger_id = None

    def trigger_button_action(self, action_id):
        if action_id == "shoot":
            self.game.weapon_manager.shoot()
        elif action_id == "reload":
            self.game.weapon_manager.start_reload()
        elif action_id == "switch":
            self.game.weapon_manager.switch_weapon()
        elif action_id == "interact":
            self.game.player.interact()
        elif action_id == "grenade":
            self.game.weapon_manager.throw_grenade()
        elif action_id == "medkit":
            self.game.weapon_manager.use_medkit()

    def is_shoot_held(self):
        for btn in self.buttons:
            if btn.action_id == "shoot":
                return btn.is_pressed
        return False

    def get_movement_input(self):
        return self.joystick.move_vector

    def get_and_reset_look_delta(self):
        delta = self.look_delta
        self.look_delta = 0.0
        return delta

    def draw(self, screen):
        self.joystick.draw(screen)
        for btn in self.buttons:
            font = self.large_font if btn.action_id == "shoot" else self.font
            btn.draw(screen, font)
