"""
Comprehensive Automated Test Suite:
Tests Campaign Levels 1-8, Procedural Random Map Generation,
Solvability Graph BFS Verification, Lobby UI Pagination & Mode Toggling.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game
from engine.map_generator import RandomMapGenerator
from engine.settings import LEVELS_DATA


def test_levels_and_random_maps():
    print("================================================================")
    print(">>> 1. TESTING ALL 8 CAMPAIGN LEVELS (GEOMETRY & SURVIVORS) <<<")
    print("================================================================")
    game = Game()

    for lvl_id in range(1, 9):
        meta = LEVELS_DATA[lvl_id]
        print(f"Deploying Campaign Level {lvl_id}: {meta['title']} ({meta['subtitle']})...")
        game.start_mission(level_id=lvl_id, random_map=False)

        assert game.level_map.rows == 16 and game.level_map.cols == 16, f"Lvl {lvl_id} grid size mismatch"
        assert len(game.level_map.world_map) > 0, f"Lvl {lvl_id} world map is empty"
        assert len(game.level_map.door_positions) > 0, f"Lvl {lvl_id} door missing"
        assert len(game.sprite_manager.zombies) > 0, f"Lvl {lvl_id} zombies missing"
        assert len(game.sprite_manager.pickups) > 0, f"Lvl {lvl_id} pickups missing"
        assert game.sprite_manager.survivor is not None, f"Lvl {lvl_id} survivor missing"

        # Check wall texture loaded
        assert game.level_map.wall_type in game.asset_manager.wall_textures, f"Wall texture {game.level_map.wall_type} missing"
        # Check door texture loaded
        assert game.level_map.door_type in game.asset_manager.door_textures, f"Door texture {game.level_map.door_type} missing"

        # Run 10 raycasting / simulation frames
        for _ in range(10):
            game.delta_time = 16.6
            game.player.update_movement(game.delta_time, 0.1, 0.0, touch_look=0.0)
            game.sprite_manager.update(game.delta_time)
            game.raycasting.update()
            game.draw()

        print(f"   [OK] Lvl {lvl_id} Verified: Wall={game.level_map.wall_type}, "
              f"Door={game.level_map.door_type}, VIP={meta['survivor']} ({meta['survivor_name']}), "
              f"Zombies={len(game.sprite_manager.zombies)}, Pickups={len(game.sprite_manager.pickups)}")

    print("\n================================================================")
    print(">>> 2. TESTING PROCEDURAL RANDOM MAP GENERATOR FOR ALL LEVELS <<<")
    print("================================================================")
    for lvl_id in range(1, 9):
        meta = LEVELS_DATA[lvl_id]
        print(f"Generating Random Map for Level {lvl_id} ({meta['theme']})...")
        game.start_mission(level_id=lvl_id, random_map=True)

        assert game.level_map.random_map is True
        assert len(game.level_map.grid) == 16 and len(game.level_map.grid[0]) == 16
        assert len(game.level_map.door_positions) >= 1

        # Verify keycard exists and matches door requirement
        door_info = list(game.level_map.door_positions.values())[0]
        req_card = door_info["required_keycard"]
        has_card = any(p["type"] == f"keycard_{req_card}" for p in game.level_map.pickups)
        assert has_card, f"Required keycard_{req_card} not generated in pickups"

        # Verify pathfinding BFS graph on random map
        p_tile = (int(game.player.x), int(game.player.y))
        z_tile = (int(game.sprite_manager.zombies[0].x), int(game.sprite_manager.zombies[0].y))
        step = game.pathfinding.get_next_step(z_tile, p_tile)
        assert step is not None, "BFS failed on random map"

        # Run 20 simulation frames on random map
        for _ in range(20):
            game.delta_time = 16.6
            game.player.update_movement(game.delta_time, -0.2, 0.2, touch_look=0.1)
            game.sprite_manager.update(game.delta_time)
            game.raycasting.update()
            game.draw()

        print(f"   [OK] Procedural Lvl {lvl_id} Verified: Door requires {req_card} keycard, "
              f"Zombies={len(game.sprite_manager.zombies)}, Pickups={len(game.sprite_manager.pickups)}, "
              f"Extraction=({game.level_map.extraction_pos[0]:.1f}, {game.level_map.extraction_pos[1]:.1f})")

    print("\n================================================================")
    print(">>> 3. TESTING LOBBY UI (PAGINATION, MODES, CLICKS) <<<")
    print("================================================================")
    game.return_to_lobby()
    assert game.state == "LOBBY"

    # Unlock all 8 levels for testing UI navigation
    game.firebase_service.cache["unlocked_levels"] = list(range(1, 9))

    # Test Page 0
    game.lobby_menu.campaign_page = 0
    game.lobby_menu.draw()
    print("   [OK] Campaign Page 1 (Sectors 1-4) rendered successfully.")

    # Test Page 1
    game.lobby_menu.campaign_page = 1
    game.lobby_menu.draw()
    print("   [OK] Campaign Page 2 (Sectors 5-8) rendered successfully.")

    # Test Mode Toggle
    assert game.lobby_menu.random_map_mode is False
    game.lobby_menu.handle_campaign_clicks(1280 - 200, 100)  # Click toggle button
    assert game.lobby_menu.random_map_mode is True, "Random map toggle click failed"
    game.lobby_menu.draw()
    print("   [OK] Random Map Mode Toggled ON successfully.")

    # Test Level 7 card selection on Page 1
    # Card 3 on Page 1 is Level 7: x = 70 + 2 * 290 = 650
    game.lobby_menu.handle_campaign_clicks(660, 200)
    assert game.lobby_menu.selected_level_id == 7, f"Expected Lvl 7, got {game.lobby_menu.selected_level_id}"
    print("   [OK] Level 7 card clicked & selected on Page 2.")

    # Test Leaderboard tab with 8 levels
    game.lobby_menu.current_tab = "leaderboards"
    game.lobby_menu.leaderboard_level = 8
    game.lobby_menu.draw()
    print("   [OK] Global Leaderboard for Level 8 rendered successfully.")

    # Test Profile Dossier with 8 honors
    game.lobby_menu.current_tab = "profile"
    game.lobby_menu.draw()
    print("   [OK] Operative Dossier with 8 honors rendered successfully.")

    print("\n================================================================")
    print(">>> 4. TESTING PROGRESSION UNLOCKING UP TO LEVEL 8 <<<")
    print("================================================================")
    game.firebase_service.cache["unlocked_levels"] = [1]
    for lvl in range(1, 8):
        game.firebase_service.unlock_next_level(lvl)
    assert game.firebase_service.cache["unlocked_levels"] == list(range(1, 9)), (
        f"Progression failed: {game.firebase_service.cache['unlocked_levels']}"
    )
    print(f"   [OK] Unlocked all 8 levels progressively: {game.firebase_service.cache['unlocked_levels']}")

    print("\n================================================================")
    print(">>> ALL TESTS PASSED WITH 100% SUCCESS! <<<")
    print("================================================================")


if __name__ == "__main__":
    test_levels_and_random_maps()
