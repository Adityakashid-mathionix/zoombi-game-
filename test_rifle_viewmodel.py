import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game

def test_rifle():
    print(">>> Testing Updated Assault Rifle Viewmodel <<<")
    game = Game()
    game.start_mission(level_id=1, primary_weapon="rifle")

    # 1. Verify frames loaded
    rifle_frames = game.asset_manager.weapon_sprites.get("rifle", [])
    assert len(rifle_frames) == 3, f"Expected 3 shooting frames, got {len(rifle_frames)}"
    print(f"   [OK] Rifle has {len(rifle_frames)} shooting frames: {[f.get_size() for f in rifle_frames]}")

    reload_frames = game.asset_manager.weapon_reload_sprites.get("rifle", [])
    assert len(reload_frames) == 3, f"Expected 3 reload frames, got {len(reload_frames)}"
    print(f"   [OK] Rifle has {len(reload_frames)} reload frames: {[f.get_size() for f in reload_frames]}")

    # 2. Test Idle Draw
    game.draw()
    print("   [OK] Idle rifle viewmodel drawn successfully")

    # 3. Test Shoot
    res = game.weapon_manager.shoot()
    assert res, "Rifle shoot returned False"
    assert game.weapon_manager.is_firing, "Rifle should be firing"
    game.draw()
    print("   [OK] Rifle firing frame 1 (muzzle flash) drawn successfully")

    game.weapon_manager.anim_frame = 2
    game.draw()
    print("   [OK] Rifle firing frame 2 (recoil & smoke) drawn successfully")

    # 4. Test Reload
    game.weapon_manager.is_firing = False
    game.weapon_manager.ammo_state["rifle"][0] = 5  # Partial clip
    game.weapon_manager.start_reload()
    assert game.weapon_manager.is_reloading, "Rifle should be reloading"
    game.draw()
    print("   [OK] Rifle reload viewmodel drawn successfully")

    # 5. Capture preview screenshot in-game
    game.weapon_manager.is_reloading = False
    game.weapon_manager.is_firing = False
    game.weapon_manager.anim_frame = 0
    game.draw()
    out_screenshot = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\2f6e3e81-fbcc-4436-8231-cf7975c45b44\rifle_ingame_idle.png"
    pg.image.save(game.screen, out_screenshot)
    print(f"   [OK] Saved in-game screenshot: {out_screenshot}")

    # Shoot frame screenshot
    game.weapon_manager.is_firing = True
    game.weapon_manager.anim_frame = 1
    game.draw()
    out_shoot_screenshot = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\2f6e3e81-fbcc-4436-8231-cf7975c45b44\rifle_ingame_shoot.png"
    pg.image.save(game.screen, out_shoot_screenshot)
    print(f"   [OK] Saved in-game shoot screenshot: {out_shoot_screenshot}")

    print("\n>>> ALL RIFLE TESTS PASSED! <<<")

if __name__ == "__main__":
    test_rifle()
