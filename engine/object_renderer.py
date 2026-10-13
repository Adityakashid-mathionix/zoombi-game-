"""
Object Renderer: 3D world scene compositor, parallax sky, ceiling/floor fills,
sorted sprite blitting, and post-processing damage flash.
"""
import math
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, COLOR_FLOOR, COLOR_CEILING
)


class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.sky_offset = 0
        self.damage_alpha = 0
        self.flash_alpha = 0

    def trigger_damage(self):
        self.damage_alpha = 210

    def trigger_flash(self, intensity=160):
        self.flash_alpha = intensity

    def draw_background(self):
        # Parallax skybox synchronized with player orientation
        sky_img = self.game.asset_manager.sky_texture
        sky_x = -int((self.game.player.angle / math.tau) * WIDTH * 2) % WIDTH
        self.screen.blit(sky_img, (sky_x - WIDTH, 0))
        self.screen.blit(sky_img, (sky_x, 0))
        self.screen.blit(sky_img, (sky_x + WIDTH, 0))

        # Floor fill (lower half)
        floor_col = self.game.level_map.meta.get("floor_color", COLOR_FLOOR)
        pg.draw.rect(self.screen, floor_col, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    def render_game_objects(self):
        # Merge wall slices and 2.5D sprite projections
        all_objects = list(self.game.raycasting.objects_to_render)
        all_objects.extend(self.game.sprite_manager.sprites_to_render)

        # Painter's algorithm: sort descending by depth (furthest rendered first)
        all_objects.sort(key=lambda t: t[0], reverse=True)

        for depth, image, pos in all_objects:
            self.screen.blit(image, pos)

    def draw_post_processing(self):
        # Blood damage overlay
        if self.damage_alpha > 0:
            blood_surf = self.game.asset_manager.blood_screen.copy()
            blood_surf.set_alpha(int(self.damage_alpha))
            self.screen.blit(blood_surf, (0, 0))
            self.damage_alpha = max(0, self.damage_alpha - 5 * (self.game.delta_time / 16.0))

        # Screen flash (e.g. muzzle blast or grenade detonation)
        if self.flash_alpha > 0:
            flash_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            flash_surf.fill((255, 230, 160, int(self.flash_alpha)))
            self.screen.blit(flash_surf, (0, 0))
            self.flash_alpha = max(0, self.flash_alpha - 15 * (self.game.delta_time / 16.0))

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_post_processing()
