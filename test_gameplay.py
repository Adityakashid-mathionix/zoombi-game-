"""
Automated End-to-End Simulation Test:
Tests Game engine initialization, Lobby UI, Raycasting renderer,
weapon firing, zombie AI, survivor rescue, and backend sync.
"""
import os
import pygame as pg

# Configure dummy video driver for headless execution if needed
os.environ["SDL_VIDEODRIVER"] = "dummy"

from main import Game

def test_engine():
    print("=== STARTING FULL GAME ENGINE INTEGRATION TEST ===")
    game = Game()
    print("[1/6] Game & Subsystems initialized successfully.")
    print(f"      Backend Firebase User: {game.firebase_service.current_user.get('display_name')}")
    print(f"      Supabase Leaderboards Loaded: {len(game.supabase_service.cache['leaderboards'])} Levels")

    # Test Lobby draw
    game.lobby_menu.draw()
    print("[2/6] Lobby screen rendered without error.")

    # Deploy Mission 1
    game.start_mission(level_id=1, primary_weapon="shotgun", tactical_item="medkit")
    print("[3/6] Level 1 deployed: Outpost Medical Bay.")
    print(f"      Player at: {game.player.pos}, Health: {game.player.health}, Armor: {game.player.armor}")
    print(f"      Survivor VIP: {game.level_map.meta['survivor']} ({game.level_map.meta['survivor_name']})")
    print(f"      Zombies in sector: {len(game.sprite_manager.zombies)}")
    print(f"      Pickups in sector: {len(game.sprite_manager.pickups)}")

    # Run 60 simulation frames
    for frame in range(60):
        # Simulate joystick movement
        game.delta_time = 16.6
        joy_x, joy_y = 0.5, -0.5
        game.player.update_movement(game.delta_time, joy_x, joy_y, touch_look=0.2)
        game.weapon_manager.update(game.delta_time)
        game.sprite_manager.update(game.delta_time)
        game.raycasting.update()
        game.hud.update(game.delta_time)
        game.draw()

    print("[4/6] 60 Raycasting & Simulation frames executed smoothly.")

    # Simulate weapon fire
    fired = game.weapon_manager.shoot()
    print(f"[5/6] Weapon fired test: Shotgun blast result = {fired}. Ammo remaining: {game.weapon_manager.ammo_state['shotgun']}")

    # Simulate Survivor rescue and extraction
    print("[6/6] Testing Survivor rescue & victory trigger...")
    game.sprite_manager.survivor.rescue()
    assert game.level_map.survivor_rescued is True, "Survivor rescue state failed"
    assert game.level_map.extraction_unlocked is True, "Extraction unlock failed"

    game.trigger_level_victory()
    assert game.state == "VICTORY", f"State should be VICTORY, got {game.state}"
    print(f"      Unlocked levels now: {game.firebase_service.cache['unlocked_levels']}")
    print(f"      Badges awarded: {[b['title'] for b in game.supabase_service.get_badges(game.firebase_service.cache['user_id'])]}")

    print("=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_engine()
