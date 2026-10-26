import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game

def test_pistol():
    print(">>> Testing Updated Tactical Pistol Viewmodel <<<")
    game = Game()
    game.start_mission(level_id=1, primary_weapon="pistol")

    # 1. Verify frames loaded
    pistol_frames = game.asset_manager.weapon_sprites.get("pistol", [])
    assert len(pistol_frames) == 3, f"Expected 3 shooting frames, got {len(pistol_frames)}"
    print(f"   [OK] Pistol has {len(pistol_frames)} shooting frames: {[f.get_size() for f in pistol_frames]}")

    reload_frames = game.asset_manager.weapon_reload_sprites.get("pistol", [])
    assert len(reload_frames) == 3, f"Expected 3 reload frames, got {len(reload_frames)}"
    print(f"   [OK] Pistol has {len(reload_frames)} reload frames: {[f.get_size() for f in reload_frames]}")

    # 2. Test Idle Draw
    game.draw()
    print("   [OK] Idle pistol viewmodel drawn successfully")

    # 3. Test Shoot
    res = game.weapon_manager.shoot()
    assert res, "Pistol shoot returned False"
    assert game.weapon_manager.is_firing, "Pistol should be firing"
    game.draw()
    print("   [OK] Pistol firing frame 1 (muzzle flash) drawn successfully")

    game.weapon_manager.anim_frame = 2
    game.draw()
    print("   [OK] Pistol firing frame 2 (recoil & smoke) drawn successfully")

    # 4. Test Reload
    game.weapon_manager.is_firing = False
    game.weapon_manager.ammo_state["pistol"][0] = 5  # Partial clip
    game.weapon_manager.start_reload()
    assert game.weapon_manager.is_reloading, "Pistol should be reloading"
    game.draw()
    print("   [OK] Pistol reload viewmodel drawn successfully")

    # 5. Capture preview screenshot in-game
    artifact_dir = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\2f6e3e81-fbcc-4436-8231-cf7975c45b44"
    game.weapon_manager.is_reloading = False
    game.weapon_manager.is_firing = False
    game.weapon_manager.anim_frame = 0
    game.draw()
    out_screenshot = os.path.join(artifact_dir, "pistol_ingame_idle.png")
    pg.image.save(game.screen, out_screenshot)
    print(f"   [OK] Saved in-game screenshot: {out_screenshot}")

    # Shoot frame screenshot
    game.weapon_manager.is_firing = True
    game.weapon_manager.anim_frame = 1
    game.draw()
    out_shoot_screenshot = os.path.join(artifact_dir, "pistol_ingame_shoot.png")
    pg.image.save(game.screen, out_shoot_screenshot)
    print(f"   [OK] Saved in-game shoot screenshot: {out_shoot_screenshot}")

    # Reload frame screenshot
    game.weapon_manager.is_firing = False
    game.weapon_manager.is_reloading = True
    game.weapon_manager.reload_start_time = pg.time.get_ticks() - 600
    game.draw()
    out_reload_screenshot = os.path.join(artifact_dir, "pistol_ingame_reload.png")
    pg.image.save(game.screen, out_reload_screenshot)
    print(f"   [OK] Saved in-game reload screenshot: {out_reload_screenshot}")

    print("\n>>> ALL PISTOL TESTS PASSED! <<<")

if __name__ == "__main__":
    test_pistol()
