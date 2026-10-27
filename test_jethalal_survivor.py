import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game

def test_jethalal_level3():
    print(">>> Testing Jethalal Gada Level 3 Survivor NPC <<<")
    game = Game()
    game.start_mission(level_id=3, primary_weapon="rifle")

    surv = game.sprite_manager.survivor
    assert surv is not None, "Survivor NPC not spawned in Level 3"
    assert len(surv.frames) >= 3, f"Expected at least 3 Jethalal sprite frames, got {len(surv.frames)}"
    print(f"   [OK] Jethalal Gada Survivor loaded with {len(surv.frames)} animated frames: {[f.get_size() for f in surv.frames]}")

    # Check custom Level 3 shouts
    assert any("JETHALAL" in s for s in surv.shouts), "Shouts should mention JETHALAL"
    assert any("BAPUJI" in s or "DAYA" in s or "GADA" in s for s in surv.shouts), "Shouts should feature iconic Jethalal panic lines"
    print(f"   [OK] Verified Jethalal's custom distress calls: {surv.shouts[0]}")

    surv_x, surv_y = surv.x, surv.y
    print(f"   [OK] Jethalal position in Level 3 map: ({surv_x}, {surv_y})")

    # Place player facing Jethalal directly looking down the hallway
    game.player.x = surv_x
    game.player.y = surv_y - 2.5
    game.player.angle = 1.5708  # Facing south towards survivor

    # Trigger shout
    surv.shout_cooldown = 0
    surv.update(dt=50)

    # Verify HUD message displayed
    msg = game.hud.message_text
    print("   [OK] Active HUD Distress Shout:", msg.encode('ascii', 'replace').decode('ascii'))
    assert msg and "JETHALAL" in msg.upper(), f"HUD message should contain JETHALAL, got {msg}"

    # Render in-game frame
    game.delta_time = 16.6
    game.raycasting.update()
    game.sprite_manager.update(game.delta_time)
    game.draw()

    artifact_dir = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\448f970f-77d0-4a2a-a8df-e8c9b47ae529"
    out_path = os.path.join(artifact_dir, "jethalal_level3_ingame.png")
    pg.image.save(game.screen, out_path)
    print(f"   [OK] Saved in-game screenshot of Jethalal Gada: {out_path}")

    # Test Rescue dialog
    surv.rescue()
    assert surv.rescued, "Survivor should be rescued"
    assert "JETHALAL" in game.hud.message_text.upper(), "Rescue HUD should mention Jethalal"
    print(f"   [OK] Rescue dialog verified: {game.hud.message_text.encode('ascii', 'replace').decode('ascii')}")

    # Test faster follower escort speed:
    # Corridor at (7.5, 12.5) runs along the y-axis
    game.player.x = surv_x
    game.player.y = surv_y - 4.0
    old_y = surv.y
    surv.update(dt=100)
    moved_dist = abs(surv.y - old_y)
    print(f"   [OK] Rescued Jethalal fast follower escort moved {moved_dist:.4f} units along y in 100ms")
    # Verify speed is high (0.0036 * 100 = 0.36)
    assert moved_dist > 0.30, f"Expected fast escort movement > 0.30, got {moved_dist:.4f}"

    print("\n>>> ALL JETHALAL GADA LEVEL 3 SURVIVOR NPC TESTS PASSED! <<<")

if __name__ == "__main__":
    test_jethalal_level3()
