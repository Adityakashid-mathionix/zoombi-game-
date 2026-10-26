import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game

def test_king_boss():
    print(">>> Testing Zombie King Boss in Level 8 <<<")
    game = Game()
    game.start_mission(level_id=8, random_map=False)

    # 1. Verify King zombie exists in Level 8
    king = next((z for z in game.sprite_manager.zombies if z.zombie_type == "king"), None)
    assert king is not None, "King zombie not found in Level 8!"
    print(f"[OK] Found Zombie King at ({king.x}, {king.y}) with HP={king.health}, MaxHP={king.max_health}, Scale={king.scale}")

    # 2. Check sprite frames
    assert "king" in game.asset_manager.zombie_sprites, "King sprites not loaded in asset manager!"
    for state in ("idle", "walk", "attack", "death"):
        frames = game.asset_manager.zombie_sprites["king"][state]
        assert len(frames) > 0, f"No frames for king {state}"
        # Verify first frame is a valid surface with proper size
        f0 = frames[0]
        assert f0.get_width() == 384 and f0.get_height() == 384, f"Frame size unexpected: {f0.get_size()}"
        print(f"   [OK] King state '{state}' has {len(frames)} valid frames ({f0.get_width()}x{f0.get_height()})")

    # 3. Check King sounds
    for s_name in ("zombie_king_shout", "zombie_king_laugh", "zombie_king_attack", "zombie_king_death"):
        assert s_name in game.sound_manager.sounds, f"Sound {s_name} not loaded in sound manager!"
        snd = game.sound_manager.sounds[s_name]
        assert snd.get_length() > 0.5, f"Sound {s_name} empty"
        print(f"   [OK] Sound '{s_name}' loaded ({snd.get_length():.2f}s)")

    # 4. Proximity / Shout test
    # Teleport player near king
    game.player.x = king.x + 2.0
    game.player.y = king.y
    game.delta_time = 16.6
    king.update(game.delta_time)
    assert king.has_shouted, "King did not shout upon player approach!"
    assert "I AM THE KING" in game.hud.message_text, f"HUD message expected to contain shout"
    clean_msg = game.hud.message_text.encode('ascii', errors='replace').decode('ascii')
    print(f"   [OK] Proximity Shout triggered: HUD message = '{clean_msg}'")

    # 5. Combat / Damage test
    initial_hp = king.health
    king.take_damage(60)
    assert king.health == initial_hp - 60, "King did not take damage properly"
    print(f"   [OK] King took damage: {initial_hp} -> {king.health} HP")

    # 6. Render test with Boss Health Bar
    game.draw()
    print("   [OK] Game draw with Boss Health Bar executed without error")

    # 7. Slay King
    king.take_damage(king.health + 100)
    assert not king.alive, "King should be dead"
    assert king.state == "death", "King state should be death"
    assert "SLAIN" in game.hud.message_text or "DESTROYED" in game.hud.message_text
    clean_death_msg = game.hud.message_text.encode('ascii', errors='replace').decode('ascii')
    print(f"   [OK] King death handled: HUD message = '{clean_death_msg}'")

    # Final render after boss slain
    game.draw()
    print("   [OK] Game draw post-slain executed successfully")

    print("\n>>> ALL ZOMBIE KING BOSS TESTS PASSED! <<<")

if __name__ == "__main__":
    test_king_boss()
