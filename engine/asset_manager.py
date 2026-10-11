"""
Asset Manager & Procedural Graphic Generator.
Generates and loads all textures, 2.5D sprites, weapons, pickups, and mobile UI overlays.
"""
import os
import math
import random
from PIL import Image, ImageDraw
import pygame as pg
from engine.settings import RES, WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, TEXTURE_SIZE, HALF_TEXTURE_SIZE


class AssetGenerator:
    """Procedurally creates retro pixel-art style textures and sprites."""

    @staticmethod
    def create_wall_medical(path):
        """Level 1: Medical Bay tiles with clinical teal/white pattern & blood stains."""
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (210, 225, 230, 255))
        draw = ImageDraw.Draw(img)
        # Tile grid
        grid_size = 32
        for x in range(0, TEXTURE_SIZE, grid_size):
            draw.line([(x, 0), (x, TEXTURE_SIZE)], fill=(150, 175, 185), width=2)
        for y in range(0, TEXTURE_SIZE, grid_size):
            draw.line([(0, y), (TEXTURE_SIZE, y)], fill=(150, 175, 185), width=2)
        # Emergency Red Cross Stripe across middle
        draw.rectangle([(0, 110), (TEXTURE_SIZE, 146)], fill=(190, 30, 40))
        draw.rectangle([(116, 90), (140, 166)], fill=(240, 240, 245))
        draw.rectangle([(104, 116), (152, 140)], fill=(240, 240, 245))
        # Blood splatter details
        draw.ellipse([(60, 160), (95, 195)], fill=(140, 15, 20, 220))
        draw.ellipse([(75, 185), (85, 220)], fill=(120, 10, 15, 200))
        draw.ellipse([(180, 50), (205, 80)], fill=(130, 12, 18, 180))
        img.save(path)

    @staticmethod
    def create_wall_subway(path):
        """Level 2: Abandoned subway grime, cracked tiles and transit signs."""
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (45, 48, 52, 255))
        draw = ImageDraw.Draw(img)
        # Subway dirty brick tiles
        tile_w, tile_h = 64, 28
        row = 0
        for y in range(0, TEXTURE_SIZE, tile_h):
            offset = (row % 2) * (tile_w // 2)
            for x in range(-offset, TEXTURE_SIZE, tile_w):
                draw.rectangle([(x + 1, y + 1), (x + tile_w - 2, y + tile_h - 2)], fill=(65 + (x % 15), 68, 70))
                draw.line([(x, y), (x + tile_w, y)], fill=(25, 25, 28), width=2)
                draw.line([(x, y), (x, y + tile_h)], fill=(25, 25, 28), width=2)
            row += 1
        # Yellow transit warning band
        draw.rectangle([(0, 115), (TEXTURE_SIZE, 145)], fill=(230, 185, 25))
        draw.rectangle([(20, 122), (236, 138)], fill=(20, 20, 25))
        # Danger high voltage lightning bolt
        draw.polygon([(128, 80), (120, 105), (132, 105), (124, 130), (138, 100), (128, 100)], fill=(255, 220, 30))
        # Grime drips
        draw.line([(40, 0), (45, 90)], fill=(20, 25, 22), width=3)
        draw.line([(190, 0), (195, 110)], fill=(20, 25, 22), width=4)
        img.save(path)

    @staticmethod
    def create_wall_barricade(path):
        """Level 3: Concrete barricades, barbed wire and biohazard quarantine marks."""
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (80, 82, 85, 255))
        draw = ImageDraw.Draw(img)
        # Concrete slabs with expansion seams
        draw.line([(0, 85), (TEXTURE_SIZE, 85)], fill=(40, 40, 42), width=3)
        draw.line([(0, 170), (TEXTURE_SIZE, 170)], fill=(40, 40, 42), width=3)
        draw.line([(128, 0), (128, 85)], fill=(40, 40, 42), width=3)
        draw.line([(64, 85), (64, 170)], fill=(40, 40, 42), width=3)
        draw.line([(192, 85), (192, 170)], fill=(40, 40, 42), width=3)
        draw.line([(128, 170), (128, 256)], fill=(40, 40, 42), width=3)
        # Sandbag cluster along bottom
        for bx in range(10, TEXTURE_SIZE - 20, 45):
            draw.ellipse([(bx, 205), (bx + 55, 250)], fill=(145, 125, 80))
            draw.ellipse([(bx + 5, 210), (bx + 50, 245)], fill=(160, 140, 95))
        # Spray painted Biohazard stencil
        draw.ellipse([(98, 98), (158, 158)], outline=(220, 40, 40), width=4)
        draw.ellipse([(113, 113), (143, 143)], fill=(220, 40, 40))
        img.save(path)

    @staticmethod
    def create_wall_chemical(path):
        """Level 4: Industrial chemical plant with yellow-black hazard stripes and toxic pipes."""
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (55, 58, 62, 255))
        draw = ImageDraw.Draw(img)
        # Steel rivets & plates
        draw.rectangle([(10, 10), (246, 246)], outline=(35, 38, 42), width=4)
        for rx in (20, 236):
            for ry in (20, 75, 130, 185, 236):
                draw.ellipse([(rx - 4, ry - 4), (rx + 4, ry + 4)], fill=(120, 125, 130))
        # Yellow and black hazard diagonal stripes across header
        stripe_w = 24
        for sx in range(-TEXTURE_SIZE, TEXTURE_SIZE * 2, stripe_w * 2):
            draw.polygon([(sx, 0), (sx + stripe_w, 0), (sx + stripe_w - 40, 40), (sx - 40, 40)], fill=(240, 210, 20))
            draw.polygon([(sx + stripe_w, 0), (sx + stripe_w * 2, 0), (sx + stripe_w * 2 - 40, 40), (sx + stripe_w - 40, 40)], fill=(20, 20, 22))
        # Glowing green toxic conduit pipes
        draw.rectangle([(40, 80), (70, 246)], fill=(30, 70, 40))
        draw.rectangle([(46, 80), (64, 246)], fill=(50, 220, 80))
        draw.rectangle([(186, 80), (216, 246)], fill=(30, 70, 40))
        draw.rectangle([(192, 80), (210, 246)], fill=(50, 220, 80))
        img.save(path)

    @staticmethod
    def create_wall_lab(path):
        """Level 5: High-tech subterranean BioCorp research lab."""
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (25, 30, 40, 255))
        draw = ImageDraw.Draw(img)
        # Hexagonal tech pattern
        draw.rectangle([(8, 8), (248, 248)], outline=(60, 75, 100), width=3)
        draw.rectangle([(20, 20), (236, 120)], fill=(18, 22, 30), outline=(40, 180, 240), width=2)
        # Server rack LEDs
        for lx in range(35, 225, 25):
            for ly in range(35, 105, 18):
                led_col = (0, 230, 255) if (lx + ly) % 5 == 0 else (40, 220, 80) if (lx * ly) % 3 == 0 else (240, 60, 60)
                draw.rectangle([(lx, ly), (lx + 12, ly + 8)], fill=led_col)
        # Cryo containment glass window with mutant silhouette
        draw.rectangle([(30, 140), (226, 236)], fill=(10, 45, 65), outline=(0, 220, 255), width=3)
        draw.ellipse([(108, 160), (148, 205)], fill=(15, 80, 100))
        # Neon blue power conduit
        draw.line([(0, 130), (TEXTURE_SIZE, 130)], fill=(0, 210, 255), width=3)
        img.save(path)

    @staticmethod
    def create_wall_door(path, color_rgb=(220, 40, 50), label="LOCKED"):
        """Reinforced Security Door with colored electronic keycard reader."""
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (50, 55, 60, 255))
        draw = ImageDraw.Draw(img)
        # Metal frame
        draw.rectangle([(12, 0), (244, TEXTURE_SIZE)], fill=(65, 70, 78), outline=(30, 32, 36), width=4)
        # Door panels
        draw.rectangle([(30, 20), (226, 110)], fill=(45, 48, 54), outline=(85, 90, 100), width=3)
        draw.rectangle([(30, 130), (226, 236)], fill=(45, 48, 54), outline=(85, 90, 100), width=3)
        # Electronic Keypad & Scanner in center
        draw.rectangle([(96, 95), (160, 145)], fill=(15, 15, 18), outline=color_rgb, width=3)
        # Keycard swipe slot
        draw.rectangle([(106, 105), (150, 115)], fill=color_rgb)
        # Status LED light
        draw.ellipse([(120, 125), (136, 141)], fill=color_rgb)
        # Warning hazard border
        draw.rectangle([(0, 0), (12, TEXTURE_SIZE)], fill=(230, 190, 20))
        draw.rectangle([(244, 0), (TEXTURE_SIZE, TEXTURE_SIZE)], fill=(230, 190, 20))
        img.save(path)

    @staticmethod
    def create_wall_extraction(path):
        """Extraction Zone / Evacuation Portal."""
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), (20, 35, 25, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(10, 10), (246, 246)], outline=(50, 240, 110), width=6)
        # Bright green chevron arrows pointing out
        for y in range(40, 220, 45):
            draw.polygon([(80, y + 25), (128, y), (176, y + 25), (160, y + 25), (128, y + 10), (96, y + 25)], fill=(50, 255, 120))
        # Text stencil block
        draw.rectangle([(35, 105), (221, 145)], fill=(10, 50, 25), outline=(50, 255, 120), width=2)
        draw.rectangle([(45, 115), (211, 135)], fill=(50, 255, 120))
        img.save(path)

    @staticmethod
    def create_sky(path):
        """Apocalyptic dark horizon sky with blood moon and smog."""
        img = Image.new("RGBA", (WIDTH, HALF_HEIGHT), (16, 14, 22, 255))
        draw = ImageDraw.Draw(img)
        # Dark smoky gradient
        for y in range(HALF_HEIGHT):
            ratio = y / HALF_HEIGHT
            r = int(22 + ratio * 55)
            g = int(14 + ratio * 15)
            b = int(24 + ratio * 15)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        # Blood Moon in sky
        moon_center = (WIDTH // 3, HALF_HEIGHT // 3)
        draw.ellipse([(moon_center[0] - 45, moon_center[1] - 45), 
                      (moon_center[0] + 45, moon_center[1] + 45)], fill=(225, 55, 45, 240))
        draw.ellipse([(moon_center[0] - 35, moon_center[1] - 35), 
                      (moon_center[0] + 35, moon_center[1] + 35)], fill=(245, 80, 60, 255))
        # Distant ruined city skyline silhouettes
        x = 0
        while x < WIDTH:
            b_width = random.randint(30, 90)
            b_height = random.randint(40, 120)
            draw.rectangle([(x, HALF_HEIGHT - b_height), (x + b_width, HALF_HEIGHT)], fill=(10, 8, 14, 255))
            x += b_width - random.randint(5, 15)
        img.save(path)

    @staticmethod
    def create_blood_screen(path):
        """Vignette blood splatter damage overlay."""
        img = Image.new("RGBA", RES, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Red peripheral vignette
        for i in range(120):
            alpha = int(220 * (1 - i / 120) ** 1.8)
            draw.rectangle([(i, i), (WIDTH - i, HEIGHT - i)], outline=(190, 10, 15, alpha), width=2)
        # Splatters
        random.seed(42)
        for _ in range(40):
            bx = random.choice([random.randint(0, 250), random.randint(WIDTH - 250, WIDTH)])
            by = random.randint(0, HEIGHT)
            br = random.randint(15, 60)
            draw.ellipse([(bx - br, by - br), (bx + br, by + br)], fill=(160, 12, 18, random.randint(120, 210)))
        img.save(path)

    @classmethod
    def create_zombie_sprites(cls, base_dir="assets/sprites/zombies"):
        """Generate animated 2.5D frames for Walker, Runner, Spitter, and Brute."""
        types = {
            "walker": {"skin": (95, 120, 100), "clothes": (60, 65, 80), "size": 1.0, "eyes": (220, 40, 40)},
            "runner": {"skin": (130, 90, 85), "clothes": (40, 40, 45), "size": 0.9, "eyes": (255, 180, 20)},
            "spitter": {"skin": (60, 140, 75), "clothes": (50, 70, 55), "size": 1.05, "eyes": (50, 255, 60)},
            "brute": {"skin": (85, 75, 95), "clothes": (35, 35, 40), "size": 1.35, "eyes": (255, 30, 30)},
        }
        for z_name, props in types.items():
            z_dir = os.path.join(base_dir, z_name)
            os.makedirs(z_dir, exist_ok=True)
            for state in ("idle", "walk", "attack", "death"):
                state_dir = os.path.join(z_dir, state)
                os.makedirs(state_dir, exist_ok=True)
                num_frames = 4 if state in ("walk", "death") else 2
                for frame_idx in range(num_frames):
                    frame_path = os.path.join(state_dir, f"{frame_idx}.png")
                    if os.path.exists(frame_path):
                        continue
                    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(img)
                    skin = props["skin"]
                    clothes = props["clothes"]
                    eyes = props["eyes"]
                    scale = props["size"]

                    # Base dimensions
                    cx, cy = 128, 140
                    w_mod = math.sin(frame_idx * math.pi / 2) * 8 if state == "walk" else 0
                    h_mod = -8 if state == "attack" and frame_idx == 1 else 0

                    if state == "death":
                        # Collapsing / puddle sprite
                        collapse = frame_idx * 28
                        draw.ellipse([(60, 200 - collapse // 4), (196, 240)], fill=(120, 15, 20, 180))  # Blood pool
                        draw.ellipse([(80 - collapse // 2, 190 + collapse // 2), 
                                      (176 + collapse // 2, 235)], fill=clothes)
                        draw.ellipse([(100, 210), (156, 240)], fill=skin)
                    else:
                        # Head
                        head_r = int(24 * scale)
                        draw.ellipse([(cx - head_r, cy - int(75 * scale) + h_mod), 
                                      (cx + head_r, cy - int(27 * scale) + h_mod)], fill=skin)
                        # Glowing eyes
                        eye_y = cy - int(52 * scale) + h_mod
                        draw.rectangle([(cx - 14, eye_y), (cx - 6, eye_y + 6)], fill=eyes)
                        draw.rectangle([(cx + 6, eye_y), (cx + 14, eye_y + 6)], fill=eyes)
                        # Bloody jaw
                        draw.rectangle([(cx - 10, eye_y + 16), (cx + 10, eye_y + 24)], fill=(140, 15, 20))

                        # Torso
                        torso_w = int(36 * scale)
                        draw.rectangle([(cx - torso_w, cy - int(25 * scale) + h_mod), 
                                        (cx + torso_w, cy + int(50 * scale) + h_mod)], fill=clothes)

                        # Arms (lunging forward during attack)
                        arm_offset = 30 if state == "attack" and frame_idx == 1 else 10
                        draw.rectangle([(cx - torso_w - 14, cy - int(20 * scale) - arm_offset + h_mod), 
                                        (cx - torso_w, cy + int(35 * scale) - arm_offset + h_mod)], fill=skin)
                        draw.rectangle([(cx + torso_w, cy - int(20 * scale) - arm_offset + h_mod), 
                                        (cx + torso_w + 14, cy + int(35 * scale) - arm_offset + h_mod)], fill=skin)

                        # Legs
                        leg_w = int(14 * scale)
                        draw.rectangle([(cx - torso_w + 4 + w_mod, cy + int(50 * scale) + h_mod), 
                                        (cx - torso_w + 4 + leg_w + w_mod, 230)], fill=(30, 30, 35))
                        draw.rectangle([(cx + torso_w - 4 - leg_w - w_mod, cy + int(50 * scale) + h_mod), 
                                        (cx + torso_w - 4 - w_mod, 230)], fill=(30, 30, 35))
                    img.save(frame_path)

    @classmethod
    def create_survivor_sprites(cls, base_dir="assets/sprites/survivors"):
        """Generate animated sprites for the 5 survivors with unique visual uniforms."""
        survivors = {
            1: {"name": "doctor", "coat": (240, 245, 248), "accent": (220, 30, 40), "head": "hair_dark"},
            2: {"name": "engineer", "coat": (245, 140, 20), "accent": (255, 220, 30), "head": "hard_hat"},
            3: {"name": "scout", "coat": (65, 80, 60), "accent": (40, 45, 35), "head": "beret"},
            4: {"name": "virologist", "coat": (235, 210, 30), "accent": (40, 180, 240), "head": "hazmat_visor"},
            5: {"name": "scientist", "coat": (225, 230, 235), "accent": (40, 50, 80), "head": "glasses"},
        }
        for lvl_id, data in survivors.items():
            s_dir = os.path.join(base_dir, data["name"])
            os.makedirs(s_dir, exist_ok=True)
            for frame_idx in range(2):
                frame_path = os.path.join(s_dir, f"{frame_idx}.png")
                if os.path.exists(frame_path):
                    continue
                img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                coat = data["coat"]
                accent = data["accent"]
                bob = -3 if frame_idx == 1 else 0

                cx, cy = 128, 140 + bob
                # Head
                draw.ellipse([(cx - 24, cy - 72), (cx + 24, cy - 24)], fill=(240, 200, 170))
                # Headgear / hair
                if data["head"] == "hard_hat":
                    draw.ellipse([(cx - 28, cy - 80), (cx + 28, cy - 50)], fill=(255, 215, 20))
                elif data["head"] == "hazmat_visor":
                    draw.ellipse([(cx - 28, cy - 80), (cx + 28, cy - 35)], fill=(235, 210, 30))
                    draw.rectangle([(cx - 18, cy - 58), (cx + 18, cy - 40)], fill=(40, 200, 240))
                elif data["head"] == "beret":
                    draw.ellipse([(cx - 26, cy - 80), (cx + 22, cy - 52)], fill=(30, 45, 30))
                elif data["head"] == "glasses":
                    draw.rectangle([(cx - 16, cy - 54), (cx - 4, cy - 44)], outline=(20, 20, 25), width=2)
                    draw.rectangle([(cx + 4, cy - 54), (cx + 16, cy - 44)], outline=(20, 20, 25), width=2)
                    draw.line([(cx - 4, cy - 49), (cx + 4, cy - 49)], fill=(20, 20, 25), width=2)
                else:
                    draw.ellipse([(cx - 24, cy - 78), (cx + 24, cy - 52)], fill=(50, 35, 25))

                # Torso uniform
                draw.rectangle([(cx - 32, cy - 24), (cx + 32, cy + 46)], fill=coat)
                # Accent badge / vest / stripes
                if data["name"] == "doctor":
                    # Red cross armband
                    draw.rectangle([(cx - 32, cy - 6), (cx - 20, cy + 12)], fill=accent)
                    draw.line([(cx - 28, cy - 2), (cx - 24, cy + 8)], fill=(255, 255, 255), width=2)
                elif data["name"] == "engineer":
                    # Reflective silver bands
                    draw.line([(cx - 32, cy + 5), (cx + 32, cy + 5)], fill=(230, 230, 240), width=4)
                    draw.line([(cx - 32, cy + 25), (cx + 32, cy + 25)], fill=(230, 230, 240), width=4)
                elif data["name"] == "scientist":
                    # Holding classified briefcase
                    draw.rectangle([(cx + 26, cy + 15), (cx + 46, cy + 40)], fill=(35, 25, 20), outline=(200, 160, 40), width=2)

                # Waving / signaling arm
                if frame_idx == 1:
                    draw.line([(cx + 32, cy - 10), (cx + 52, cy - 45)], fill=coat, width=12)
                    draw.ellipse([(cx + 48, cy - 55), (cx + 60, cy - 43)], fill=(240, 200, 170))
                else:
                    draw.rectangle([(cx + 32, cy - 15), (cx + 44, cy + 30)], fill=coat)

                # Legs
                draw.rectangle([(cx - 28, cy + 46), (cx - 8, 230)], fill=(40, 45, 55))
                draw.rectangle([(cx + 8, cy + 46), (cx + 28, 230)], fill=(40, 45, 55))
                img.save(frame_path)

    @classmethod
    def create_weapon_viewmodels(cls, base_dir="assets/sprites/weapons"):
        """Create first person weapon viewmodels (Pistol, Shotgun, Rifle) with fire & reload animations."""
        os.makedirs(base_dir, exist_ok=True)
        # 1. Pistol
        p_dir = os.path.join(base_dir, "pistol")
        os.makedirs(p_dir, exist_ok=True)
        for i in range(3):
            path = os.path.join(p_dir, f"{i}.png")
            if not os.path.exists(path):
                img = Image.new("RGBA", (320, 280), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                # Hands
                draw.ellipse([(100, 180), (220, 310)], fill=(210, 175, 145))
                # Gun body
                slide_kick = -12 if i == 1 else 0
                draw.rectangle([(138, 90 + slide_kick), (182, 210)], fill=(45, 48, 52), outline=(20, 22, 25), width=2)
                draw.rectangle([(144, 75 + slide_kick), (176, 95 + slide_kick)], fill=(30, 32, 35))
                # Muzzle flash on frame 1
                if i == 1:
                    draw.ellipse([(130, 25), (190, 85)], fill=(255, 230, 80, 230))
                    draw.ellipse([(145, 40), (175, 75)], fill=(255, 255, 255, 255))
                img.save(path)

        # 2. Shotgun
        s_dir = os.path.join(base_dir, "shotgun")
        os.makedirs(s_dir, exist_ok=True)
        for i in range(4):
            path = os.path.join(s_dir, f"{i}.png")
            if not os.path.exists(path):
                img = Image.new("RGBA", (380, 320), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                kick = -25 if i == 1 else 0
                # Heavy barrels
                draw.rectangle([(160, 60 + kick), (220, 250)], fill=(50, 52, 58), outline=(25, 28, 30), width=3)
                draw.rectangle([(170, 45 + kick), (210, 65 + kick)], fill=(35, 38, 40))
                # Wooden fore-end pump
                pump_y = 175 if i == 2 else 150
                draw.rectangle([(152, pump_y), (228, pump_y + 45)], fill=(120, 75, 45))
                # Hands
                draw.ellipse([(110, pump_y + 10), (170, pump_y + 60)], fill=(210, 175, 145))
                draw.ellipse([(195, 210), (275, 310)], fill=(210, 175, 145))
                # Huge muzzle blast on frame 1
                if i == 1:
                    draw.ellipse([(120, -10), (260, 65)], fill=(255, 195, 40, 235))
                    draw.ellipse([(150, 5), (230, 50)], fill=(255, 255, 255, 255))
                img.save(path)

        # 3. Assault Rifle
        r_dir = os.path.join(base_dir, "rifle")
        os.makedirs(r_dir, exist_ok=True)
        for i in range(3):
            path = os.path.join(r_dir, f"{i}.png")
            if not os.path.exists(path):
                img = Image.new("RGBA", (360, 300), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                kick = -10 if i == 1 else 0
                # Barrel & tactical receiver
                draw.rectangle([(155, 50 + kick), (205, 230)], fill=(38, 42, 46), outline=(18, 20, 22), width=2)
                draw.rectangle([(170, 25 + kick), (190, 55 + kick)], fill=(25, 28, 30))
                # Flash suppressor & scope rail
                draw.rectangle([(165, 80 + kick), (195, 110 + kick)], fill=(50, 55, 60))
                # Curved magazine
                draw.polygon([(170, 180), (190, 180), (180, 260), (160, 260)], fill=(25, 25, 28))
                # Hands
                draw.ellipse([(115, 150), (165, 200)], fill=(210, 175, 145))
                draw.ellipse([(185, 200), (255, 290)], fill=(210, 175, 145))
                # Rapid flash
                if i == 1:
                    draw.ellipse([(145, 0), (215, 35)], fill=(255, 220, 50, 240))
                    draw.ellipse([(165, 8), (195, 25)], fill=(255, 255, 255, 255))
                img.save(path)

    @classmethod
    def create_pickups_and_ui(cls, base_dir="assets/sprites/pickups", ui_dir="assets/ui"):
        """Create world pickups and UI icons (Medkit, Ammo, Armor, Keycards, Grenade, Stim, Controls)."""
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(ui_dir, exist_ok=True)

        # Medkit Pickup
        med_path = os.path.join(base_dir, "medkit.png")
        if not os.path.exists(med_path):
            img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rectangle([(20, 35), (108, 105)], fill=(240, 245, 245), outline=(160, 170, 175), width=3)
            draw.rectangle([(48, 18), (80, 36)], outline=(160, 170, 175), width=4)  # Handle
            draw.rectangle([(56, 50), (72, 90)], fill=(225, 30, 40))
            draw.rectangle([(36, 62), (92, 78)], fill=(225, 30, 40))
            img.save(med_path)

        # Ammo Crate Pickup
        ammo_path = os.path.join(base_dir, "ammo.png")
        if not os.path.exists(ammo_path):
            img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rectangle([(18, 40), (110, 108)], fill=(65, 80, 55), outline=(40, 50, 35), width=3)
            # Gold bullet stencil
            draw.polygon([(52, 60), (64, 48), (76, 60)], fill=(240, 195, 40))
            draw.rectangle([(52, 60), (76, 92)], fill=(240, 195, 40))
            img.save(ammo_path)

        # Armor Vest Pickup
        armor_path = os.path.join(base_dir, "armor.png")
        if not os.path.exists(armor_path):
            img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.polygon([(30, 30), (52, 18), (76, 18), (98, 30), (108, 108), (20, 108)], fill=(45, 60, 80), outline=(25, 35, 50), width=3)
            draw.rectangle([(40, 50), (88, 92)], fill=(35, 45, 60))
            img.save(armor_path)

        # Keycards (5 colors)
        kc_colors = {
            "red": (230, 45, 55),
            "yellow": (245, 200, 35),
            "blue": (35, 145, 245),
            "green": (45, 220, 80),
            "purple": (190, 60, 245),
        }
        for kc_name, kc_col in kc_colors.items():
            kc_path = os.path.join(base_dir, f"keycard_{kc_name}.png")
            if not os.path.exists(kc_path):
                img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.rectangle([(25, 25), (103, 103)], fill=kc_col, outline=(240, 240, 245), width=3)
                draw.rectangle([(35, 40), (93, 56)], fill=(25, 25, 28))  # Magnetic stripe
                draw.rectangle([(75, 70), (93, 88)], fill=(240, 210, 40))  # Smart chip
                img.save(kc_path)

        # Frag Grenade Pickup
        grenade_path = os.path.join(base_dir, "grenade.png")
        if not os.path.exists(grenade_path):
            img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([(38, 42), (90, 106)], fill=(70, 85, 55), outline=(35, 45, 28), width=3)
            draw.rectangle([(56, 24), (72, 44)], fill=(130, 135, 140))
            draw.ellipse([(68, 20), (84, 36)], outline=(200, 200, 210), width=3)  # Pin ring
            img.save(grenade_path)

        # Adrenaline Stim Shot
        stim_path = os.path.join(base_dir, "stim.png")
        if not os.path.exists(stim_path):
            img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rectangle([(54, 30), (74, 95)], fill=(220, 230, 240), outline=(100, 120, 140), width=2)
            draw.rectangle([(58, 45), (70, 85)], fill=(0, 220, 255))  # Glowing stim fluid
            draw.line([(64, 95), (64, 115)], fill=(180, 190, 200), width=2)  # Needle
            img.save(stim_path)

        # Crosshair UI
        cross_path = os.path.join(ui_dir, "crosshair.png")
        if not os.path.exists(cross_path):
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.line([(32, 14), (32, 26)], fill=(240, 240, 250, 220), width=2)
            draw.line([(32, 38), (32, 50)], fill=(240, 240, 250, 220), width=2)
            draw.line([(14, 32), (26, 32)], fill=(240, 240, 250, 220), width=2)
            draw.line([(38, 32), (50, 32)], fill=(240, 240, 250, 220), width=2)
            draw.point((32, 32), fill=(255, 40, 50, 255))
            img.save(cross_path)


class AssetManager:
    """Loads and caches all Pygame surfaces for the 3D raycaster and 2D mobile UI."""

    def __init__(self):
        self.wall_textures = {}
        self.door_textures = {}
        self.extraction_texture = None
        self.sky_texture = None
        self.blood_screen = None
        self.crosshair = None
        self.zombie_sprites = {}
        self.survivor_sprites = {}
        self.weapon_sprites = {}
        self.pickup_sprites = {}
        self.ui_icons = {}

        # Ensure all textures are generated
        self.generate_and_load_all()

    def generate_and_load_all(self):
        tex_dir = "assets/textures"
        os.makedirs(tex_dir, exist_ok=True)

        # Build walls
        AssetGenerator.create_wall_medical(os.path.join(tex_dir, "wall_medical.png"))
        AssetGenerator.create_wall_subway(os.path.join(tex_dir, "wall_subway.png"))
        AssetGenerator.create_wall_barricade(os.path.join(tex_dir, "wall_barricade.png"))
        AssetGenerator.create_wall_chemical(os.path.join(tex_dir, "wall_chemical.png"))
        AssetGenerator.create_wall_lab(os.path.join(tex_dir, "wall_lab.png"))

        # Build door textures
        kc_colors = {
            1: (230, 45, 55),
            2: (245, 200, 35),
            3: (35, 145, 245),
            4: (45, 220, 80),
            5: (190, 60, 245),
        }
        for lvl_id, col in kc_colors.items():
            AssetGenerator.create_wall_door(os.path.join(tex_dir, f"door_level_{lvl_id}.png"), col)
        AssetGenerator.create_wall_extraction(os.path.join(tex_dir, "wall_extraction.png"))

        # Sky and overlays
        AssetGenerator.create_sky(os.path.join(tex_dir, "sky.png"))
        AssetGenerator.create_blood_screen(os.path.join(tex_dir, "blood_screen.png"))

        # Sprites
        AssetGenerator.create_zombie_sprites("assets/sprites/zombies")
        AssetGenerator.create_survivor_sprites("assets/sprites/survivors")
        AssetGenerator.create_weapon_viewmodels("assets/sprites/weapons")
        AssetGenerator.create_pickups_and_ui("assets/sprites/pickups", "assets/ui")

        # Now load into Pygame surfaces
        self.load_surfaces()

    def load_texture(self, path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        """Load image as Pygame Alpha Surface and scale to resolution."""
        if not os.path.exists(path):
            surf = pg.Surface(res, pg.SRCALPHA)
            surf.fill((180, 50, 180))  # Magenta placeholder
            return surf
        try:
            tex = pg.image.load(path).convert_alpha()
            return pg.transform.scale(tex, res)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            surf = pg.Surface(res, pg.SRCALPHA)
            surf.fill((180, 50, 180))
            return surf

    def load_surfaces(self):
        tex_dir = "assets/textures"
        # 1. Wall textures mapping by ID:
        # 1: Medical, 2: Subway, 3: Barricade, 4: Chemical, 5: Lab
        self.wall_textures = {
            1: self.load_texture(os.path.join(tex_dir, "wall_medical.png")),
            2: self.load_texture(os.path.join(tex_dir, "wall_subway.png")),
            3: self.load_texture(os.path.join(tex_dir, "wall_barricade.png")),
            4: self.load_texture(os.path.join(tex_dir, "wall_chemical.png")),
            5: self.load_texture(os.path.join(tex_dir, "wall_lab.png")),
        }

        # Door textures: mapped by 101, 102, 103, 104, 105
        for lvl_id in range(1, 6):
            self.door_textures[100 + lvl_id] = self.load_texture(os.path.join(tex_dir, f"door_level_{lvl_id}.png"))

        # Extraction tile: mapped by 99
        self.extraction_texture = self.load_texture(os.path.join(tex_dir, "wall_extraction.png"))

        # Sky & Blood screen
        self.sky_texture = self.load_texture(os.path.join(tex_dir, "sky.png"), (WIDTH, HALF_HEIGHT))
        self.blood_screen = self.load_texture(os.path.join(tex_dir, "blood_screen.png"), RES)
        self.crosshair = self.load_texture("assets/ui/crosshair.png", (48, 48))

        # Pickups
        p_dir = "assets/sprites/pickups"
        self.pickup_sprites = {
            "medkit": self.load_texture(os.path.join(p_dir, "medkit.png"), (128, 128)),
            "ammo": self.load_texture(os.path.join(p_dir, "ammo.png"), (128, 128)),
            "armor": self.load_texture(os.path.join(p_dir, "armor.png"), (128, 128)),
            "grenade": self.load_texture(os.path.join(p_dir, "grenade.png"), (128, 128)),
            "stim": self.load_texture(os.path.join(p_dir, "stim.png"), (128, 128)),
            "keycard_red": self.load_texture(os.path.join(p_dir, "keycard_red.png"), (128, 128)),
            "keycard_yellow": self.load_texture(os.path.join(p_dir, "keycard_yellow.png"), (128, 128)),
            "keycard_blue": self.load_texture(os.path.join(p_dir, "keycard_blue.png"), (128, 128)),
            "keycard_green": self.load_texture(os.path.join(p_dir, "keycard_green.png"), (128, 128)),
            "keycard_purple": self.load_texture(os.path.join(p_dir, "keycard_purple.png"), (128, 128)),
        }

        # Load Zombie sprite frames
        z_base = "assets/sprites/zombies"
        for z_name in ("walker", "runner", "spitter", "brute"):
            self.zombie_sprites[z_name] = {}
            for state in ("idle", "walk", "attack", "death"):
                state_dir = os.path.join(z_base, z_name, state)
                frames = []
                if os.path.exists(state_dir):
                    file_names = sorted(os.listdir(state_dir))
                    for fname in file_names:
                        if fname.endswith(".png"):
                            frames.append(self.load_texture(os.path.join(state_dir, fname), (256, 256)))
                self.zombie_sprites[z_name][state] = frames if frames else [self.create_fallback_sprite((180, 40, 40))]

        # Load Survivor sprites
        s_base = "assets/sprites/survivors"
        s_map = {1: "doctor", 2: "engineer", 3: "scout", 4: "virologist", 5: "scientist"}
        for lvl_id, s_name in s_map.items():
            s_dir = os.path.join(s_base, s_name)
            frames = []
            if os.path.exists(s_dir):
                for fname in sorted(os.listdir(s_dir)):
                    if fname.endswith(".png"):
                        frames.append(self.load_texture(os.path.join(s_dir, fname), (256, 256)))
            self.survivor_sprites[lvl_id] = frames if frames else [self.create_fallback_sprite((40, 180, 240))]

        # Load Weapon Viewmodels
        w_base = "assets/sprites/weapons"
        for w_name in ("pistol", "shotgun", "rifle"):
            w_dir = os.path.join(w_base, w_name)
            frames = []
            if os.path.exists(w_dir):
                for fname in sorted(os.listdir(w_dir)):
                    if fname.endswith(".png"):
                        frames.append(pg.image.load(os.path.join(w_dir, fname)).convert_alpha())
            self.weapon_sprites[w_name] = frames

    def create_fallback_sprite(self, color):
        surf = pg.Surface((256, 256), pg.SRCALPHA)
        pg.draw.circle(surf, color, (128, 128), 80)
        return surf
