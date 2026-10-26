import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame as pg
from main import Game
from engine.settings import WEAPON_CONFIGS

def test_shotgun_and_balance():
    print(">>> Testing Shotgun Viewmodel & Rebalanced Weapon Ranges/Damages <<<")
    game = Game()
    game.start_mission(level_id=1, primary_weapon="shotgun")

    # 1. Verify shotgun frames loaded
    s_frames = game.asset_manager.weapon_sprites.get("shotgun", [])
    assert len(s_frames) == 3, f"Expected 3 shooting frames, got {len(s_frames)}"
    print(f"   [OK] Shotgun has 3 shooting frames: {[f.get_size() for f in s_frames]}")

    s_reload = game.asset_manager.weapon_reload_sprites.get("shotgun", [])
    assert len(s_reload) == 3, f"Expected 3 reload frames, got {len(s_reload)}"
    print(f"   [OK] Shotgun has 3 reload frames: {[f.get_size() for f in s_reload]}")

    # 2. Verify 2-bullet capacity & reload
    assert WEAPON_CONFIGS["shotgun"]["max_ammo"] == 2, "Shotgun max_ammo must be 2"
    assert game.weapon_manager.ammo_state["shotgun"][0] == 2, "Shotgun should start loaded with 2 shells"
    print("   [OK] Shotgun starts with 2 shells in chamber")

    # Fire shot 1
    res = game.weapon_manager.shoot()
    assert res, "Shot 1 should succeed"
    assert game.weapon_manager.ammo_state["shotgun"][0] == 1, "Should have 1 shell left"
    print("   [OK] Shot 1 fired, 1 shell remains")

    # Fire shot 2 -> empty -> auto-reload
    game.weapon_manager.last_shot_time = 0
    res = game.weapon_manager.shoot()
    assert res, "Shot 2 should succeed"
    assert game.weapon_manager.ammo_state["shotgun"][0] == 0, "Clip should be empty"
    assert game.weapon_manager.is_reloading, "Should trigger reload of 2 shells"
    print("   [OK] Shot 2 fired, auto-reload initiated for 2 shells")

    # Complete reload
    game.weapon_manager.reload_start_time = pg.time.get_ticks() - 2000
    game.weapon_manager.update_reload(pg.time.get_ticks())
    assert game.weapon_manager.ammo_state["shotgun"][0] == 2, "Should reload exactly 2 shells"
    assert not game.weapon_manager.is_reloading, "Reload should finish"
    print("   [OK] Reload completed: chamber refreshed to 2 shells")

    # 3. Test Range Limits & Damage Falloff
    class MockZombie:
        def __init__(self, x, y, hp=300):
            self.x = x
            self.y = y
            self.health = hp
            self.alive = True
            self.damage_taken = 0
            self.zombie_type = "walker"
        def take_damage(self, dmg):
            self.damage_taken += dmg
            self.health -= dmg

    game.player.x = 2.0
    game.player.y = 2.0
    game.player.angle = 0.0  # Facing east (+x direction)
    game.weapon_manager.check_wall_between = lambda x1, y1, x2, y2: False  # Pure distance test

    # Test Shotgun Range: Short Range (max 4.5m)
    # Target A at dist=1.5 (close) -> Should hit with full high damage
    target_close = MockZombie(3.5, 2.0, hp=500)
    # Target B at dist=5.5 (too far for shotgun) -> Should NOT be hit
    target_far = MockZombie(7.5, 2.0, hp=500)

    game.sprite_manager.zombies = [target_close, target_far]
    game.weapon_manager.select_weapon("shotgun")
    game.weapon_manager.ammo_state["shotgun"][0] = 2
    game.weapon_manager.last_shot_time = 0
    game.weapon_manager.shoot()

    assert target_close.damage_taken > 100, f"Close target should take heavy burst damage, got {target_close.damage_taken}"
    assert target_far.damage_taken == 0, f"Far target (dist=5.5) should be out of shotgun range, took {target_far.damage_taken}"
    print(f"   [OK] Shotgun Range Verified: close target took {target_close.damage_taken} dmg, far target took 0 dmg (out of range)")

    # Test Pistol Range: Medium Range (max 8.5m), Very Low Damage (14)
    target_pistol_mid = MockZombie(8.0, 2.0, hp=100)   # dist=6.0 (within 8.5m)
    target_pistol_far = MockZombie(12.0, 2.0, hp=100)  # dist=10.0 (beyond 8.5m)
    game.sprite_manager.zombies = [target_pistol_mid, target_pistol_far]
    game.weapon_manager.select_weapon("pistol")
    game.weapon_manager.ammo_state["pistol"][0] = 12
    game.weapon_manager.last_shot_time = 0
    game.weapon_manager.shoot()

    assert 1 <= target_pistol_mid.damage_taken <= 14, f"Pistol should do very low damage, got {target_pistol_mid.damage_taken}"
    assert target_pistol_far.damage_taken == 0, f"Pistol far target (dist=10.0) should be out of range, took {target_pistol_far.damage_taken}"
    print(f"   [OK] Pistol Range/Damage Verified: mid target took {target_pistol_mid.damage_taken} low dmg, far target took 0 dmg")

    # Test Rifle Range: Long Range (16.0m), Medium Damage (25)
    target_rifle_far = MockZombie(15.0, 2.0, hp=100)  # dist=13.0 (within 16.0m)
    game.sprite_manager.zombies = [target_rifle_far]
    game.weapon_manager.select_weapon("rifle")
    game.weapon_manager.ammo_state["rifle"][0] = 30
    game.weapon_manager.last_shot_time = 0
    game.weapon_manager.shoot()

    assert target_rifle_far.damage_taken > 15, f"Rifle should reach long range (dist=13.0) with medium damage, got {target_rifle_far.damage_taken}"
    print(f"   [OK] Rifle Range/Damage Verified: long range target (dist=13.0) took {target_rifle_far.damage_taken} medium dmg")

    # 4. Capture Visual Screenshots for Shotgun
    game.weapon_manager.select_weapon("shotgun")
    artifact_dir = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\2f6e3e81-fbcc-4436-8231-cf7975c45b44"

    # Idle
    game.weapon_manager.is_reloading = False
    game.weapon_manager.is_firing = False
    game.weapon_manager.anim_frame = 0
    game.draw()
    s_idle_path = os.path.join(artifact_dir, "shotgun_ingame_idle.png")
    pg.image.save(game.screen, s_idle_path)
    print(f"   [OK] Saved in-game screenshot: {s_idle_path}")

    # Shoot (muzzle flash)
    game.weapon_manager.is_firing = True
    game.weapon_manager.anim_frame = 1
    game.draw()
    s_shoot_path = os.path.join(artifact_dir, "shotgun_ingame_shoot.png")
    pg.image.save(game.screen, s_shoot_path)
    print(f"   [OK] Saved in-game shoot screenshot: {s_shoot_path}")

    # Reload (inserting shell)
    game.weapon_manager.is_firing = False
    game.weapon_manager.is_reloading = True
    game.weapon_manager.reload_start_time = pg.time.get_ticks() - 650
    game.draw()
    s_reload_path = os.path.join(artifact_dir, "shotgun_ingame_reload.png")
    pg.image.save(game.screen, s_reload_path)
    print(f"   [OK] Saved in-game reload screenshot: {s_reload_path}")

    print("\n>>> ALL SHOTGUN & WEAPON BALANCE TESTS PASSED! <<<")

if __name__ == "__main__":
    test_shotgun_and_balance()
