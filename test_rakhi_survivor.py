import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game

def test_rakhi():
    print(">>> Testing Miss Rakhi Level 2 Survivor NPC <<<")
    game = Game()
    game.start_mission(level_id=2, primary_weapon="rifle")

    surv = game.sprite_manager.survivor
    assert surv is not None, "Survivor NPC not spawned in Level 2"
    assert len(surv.frames) >= 3, f"Expected 3 Miss Rakhi sprite frames, got {len(surv.frames)}"
    print(f"   [OK] Miss Rakhi Survivor loaded with {len(surv.frames)} animated frames: {[f.get_size() for f in surv.frames]}")

    # Check Miss Rakhi custom scared shouts
    assert any("MISS RAKHI" in s for s in surv.shouts), "Shouts should mention Miss Rakhi"
    assert any("SCARED" in s or "SCARY" in s for s in surv.shouts), "Shouts should express fear/scared"
    print(f"   [OK] Verified Miss Rakhi's custom distress calls: {surv.shouts[0]}")

    # Position player facing Miss Rakhi in Level 2
    surv_x, surv_y = surv.x, surv.y
    print(f"   [OK] Miss Rakhi position in map: ({surv_x}, {surv_y})")

    # Place player facing Miss Rakhi directly
    game.player.x = surv_x - 2.2
    game.player.y = surv_y
    game.player.angle = 0.0  # Facing east towards survivor

    # Trigger shout
    surv.shout_cooldown = 0
    surv.update(dt=50)

    # Verify HUD message displayed
    msg = game.hud.message_text
    print("   [OK] Active HUD Distress Shout:", msg.encode('ascii', 'replace').decode('ascii'))
    assert msg and "RAKHI" in msg.upper(), f"HUD message should contain RAKHI, got {msg}"

    # Render in-game frame
    game.delta_time = 16.6
    game.raycasting.update()
    game.sprite_manager.update(game.delta_time)
    game.draw()

    artifact_dir = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\ab91508e-2d7b-4f20-b36c-4cb6c51e0b15"
    out_path = os.path.join(artifact_dir, "miss_rakhi_level2_ingame.png")
    pg.image.save(game.screen, out_path)
    print(f"   [OK] Saved in-game screenshot of Miss Rakhi: {out_path}")

    # Test Rescue dialog
    surv.rescue()
    assert surv.rescued, "Survivor should be rescued"
    assert "RAKHI" in game.hud.message_text.upper(), "Rescue HUD should mention Miss Rakhi"
    print(f"   [OK] Rescue dialog verified: {game.hud.message_text.encode('ascii', 'replace').decode('ascii')}")

    print("\n>>> ALL MISS RAKHI LEVEL 2 SURVIVOR NPC TESTS PASSED! <<<")

if __name__ == "__main__":
    test_rakhi()
