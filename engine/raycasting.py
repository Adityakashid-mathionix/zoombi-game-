"""
Raycasting Engine: High-performance DDA algorithm with door support and distance shading.
"""
import math
import pygame as pg
from engine.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, NUM_RAYS, DELTA_ANGLE,
    HALF_FOV, MAX_DEPTH, SCREEN_DIST, SCALE, TEXTURE_SIZE, HALF_TEXTURE_SIZE
)


class RayCasting:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.objects_to_render = []

    def get_objects_to_render(self):
        self.objects_to_render = []
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture_id, offset = values

            # Fetch corresponding wall or door texture
            if texture_id in self.game.asset_manager.door_textures:
                texture = self.game.asset_manager.door_textures[texture_id]
            elif texture_id == 99:
                texture = self.game.asset_manager.extraction_texture
            else:
                texture = self.game.asset_manager.wall_textures.get(
                    texture_id, self.game.asset_manager.wall_textures[1]
                )

            # Subsurface column slicing
            sub_x = int(offset * (TEXTURE_SIZE - SCALE))
            sub_x = max(0, min(TEXTURE_SIZE - SCALE, sub_x))

            proj_h = max(1, int(proj_height))

            if proj_height < HEIGHT:
                wall_column = texture.subsurface(sub_x, 0, SCALE, TEXTURE_SIZE)
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_h))
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_h // 2)
            else:
                tex_h = int(TEXTURE_SIZE * HEIGHT / proj_height)
                tex_h = max(1, min(TEXTURE_SIZE, tex_h))
                wall_column = texture.subsurface(
                    sub_x, HALF_TEXTURE_SIZE - tex_h // 2, SCALE, tex_h
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HEIGHT))
                wall_pos = (ray * SCALE, 0)

            self.objects_to_render.append((depth, wall_column, wall_pos))

    def ray_cast(self):
        self.ray_casting_result = []
        ox, oy = self.game.player.pos
        x_map, y_map = int(ox), int(oy)

        ray_angle = self.game.player.angle - HALF_FOV + 0.0001
        world_map = self.game.level_map.world_map

        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # Horizontals check
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)
            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a
            delta_depth_h = dy / sin_a
            dx_h = delta_depth_h * cos_a

            texture_hor = 1
            for _ in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in world_map:
                    texture_hor = world_map[tile_hor]
                    break
                x_hor += dx_h
                y_hor += dy
                depth_hor += delta_depth_h

            # Verticals check
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)
            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a
            delta_depth_v = dx / cos_a
            dy_v = delta_depth_v * sin_a

            texture_vert = 1
            for _ in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in world_map:
                    texture_vert = world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy_v
                depth_vert += delta_depth_v

            # Compare horizontal and vertical distance
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            # Remove fishbowl distortion
            depth *= math.cos(self.game.player.angle - ray_angle)

            # Projected slice height
            proj_height = SCREEN_DIST / (depth + 0.0001)

            self.ray_casting_result.append((depth, proj_height, texture, offset))
            ray_angle += DELTA_ANGLE

    def update(self):
        self.ray_cast()
        self.get_objects_to_render()
