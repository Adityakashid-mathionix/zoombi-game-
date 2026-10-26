import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game

def test_shlok():
    print(">>> Testing Engineer Shlok ('CR') Level 1 Survivor NPC <<<")
    game = Game()
    game.start_mission(level_id=1, primary_weapon="rifle")

    surv = game.sprite_manager.survivor
    assert surv is not None, "Survivor NPC not spawned in Level 1"
    assert len(surv.frames) >= 3, f"Expected 3 Shlok sprite frames, got {len(surv.frames)}"
    print(f"   [OK] Shlok CR Survivor loaded with {len(surv.frames)} animated frames: {[f.get_size() for f in surv.frames]}")

    # Check Shlok shouts list
    assert any("CR" in s for s in surv.shouts), "Shouts should mention CR"
    assert any("SHLOK" in s for s in surv.shouts), "Shouts should mention SHLOK"
    assert any("ENGINEER" in s for s in surv.shouts), "Shouts should mention ENGINEER"
    print(f"   [OK] Verified Shlok's custom distress calls: {surv.shouts[0]}")

    # Position player facing Shlok
    surv_x, surv_y = surv.x, surv.y
    print(f"   [OK] Shlok position in map: ({surv_x}, {surv_y})")

    # Place player 2.3 tiles away facing Shlok directly in the corridor
    game.player.x = 5.2
    game.player.y = 11.5
    game.player.angle = 0.0  # Facing east directly towards Shlok

    # Trigger shout
    surv.shout_cooldown = 0
    surv.update(dt=50)

    # Verify HUD message displayed
    msg = game.hud.message_text
    print("   [OK] Active HUD Distress Shout:", msg.encode('ascii', 'replace').decode('ascii'))
    assert msg and "SHLOK" in msg.upper(), f"HUD message should contain SHLOK, got {msg}"

    # Render in-game frame
    game.delta_time = 16.6
    game.raycasting.update()
    game.sprite_manager.update(game.delta_time)
    game.draw()

    artifact_dir = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\2f6e3e81-fbcc-4436-8231-cf7975c45b44"
    out_path = os.path.join(artifact_dir, "survivor_shlok_ingame.png")
    pg.image.save(game.screen, out_path)
    print(f"   [OK] Saved in-game screenshot of Shlok CR: {out_path}")

    print("\n>>> ALL SHLOK CR SURVIVOR NPC TESTS PASSED! <<<")

if __name__ == "__main__":
    test_shlok()
