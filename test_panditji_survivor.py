import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game

def test_panditji_level7():
    print(">>> Testing Panditji Maharaj Level 7 Survivor NPC <<<")
    game = Game()
    game.start_mission(level_id=7, primary_weapon="rifle")

    surv = game.sprite_manager.survivor
    assert surv is not None, "Survivor NPC not spawned in Level 7"
    assert len(surv.frames) >= 3, f"Expected 3 Panditji sprite frames, got {len(surv.frames)}"
    print(f"   [OK] Panditji Maharaj Survivor loaded with {len(surv.frames)} animated frames: {[f.get_size() for f in surv.frames]}")

    # Check custom Level 7 shouts
    assert any("PANDITJI" in s for s in surv.shouts), "Shouts should mention PANDITJI"
    assert any("BHAGWAN" in s or "SHIVAYA" in s for s in surv.shouts), "Shouts should have spiritual / cultural distress dialogue"
    print(f"   [OK] Verified Panditji's custom distress calls: {surv.shouts[0]}")

    surv_x, surv_y = surv.x, surv.y
    print(f"   [OK] Panditji position in map: ({surv_x}, {surv_y})")

    # Place player facing Panditji directly
    game.player.x = surv_x - 2.0
    game.player.y = surv_y
    game.player.angle = 0.0  # Facing east towards survivor

    # Trigger shout
    surv.shout_cooldown = 0
    surv.update(dt=50)

    # Verify HUD message displayed
    msg = game.hud.message_text
    print("   [OK] Active HUD Distress Shout:", msg.encode('ascii', 'replace').decode('ascii'))
    assert msg and ("PANDITJI" in msg.upper() or "BHAGWAN" in msg.upper()), f"HUD message should contain PANDITJI, got {msg}"

    # Render in-game frame
    game.delta_time = 16.6
    game.raycasting.update()
    game.sprite_manager.update(game.delta_time)
    game.draw()

    artifact_dir = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\5915c34c-d723-481c-91c2-8ab9fa5f4066"
    out_path = os.path.join(artifact_dir, "panditji_level7_ingame.png")
    pg.image.save(game.screen, out_path)
    print(f"   [OK] Saved in-game screenshot of Panditji Maharaj: {out_path}")

    # Test Rescue dialog
    surv.rescue()
    assert surv.rescued, "Survivor should be rescued"
    assert "PANDITJI" in game.hud.message_text.upper() or "MAHADEV" in game.hud.message_text.upper(), "Rescue HUD should mention Panditji / Mahadev"
    print(f"   [OK] Rescue dialog verified: {game.hud.message_text.encode('ascii', 'replace').decode('ascii')}")

    print("\n>>> ALL PANDITJI MAHARAJ LEVEL 7 SURVIVOR NPC TESTS PASSED! <<<")

if __name__ == "__main__":
    test_panditji_level7()
