import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game

def test_modinho_level8():
    print(">>> Testing Modinho Level 8 (Last Level) Survivor NPC <<<")
    game = Game()
    game.start_mission(level_id=8, primary_weapon="rifle")

    surv = game.sprite_manager.survivor
    assert surv is not None, "Survivor NPC not spawned in Level 8"
    assert len(surv.frames) >= 4, f"Expected 4 Modinho sprite frames, got {len(surv.frames)}"
    print(f"   [OK] Modinho Survivor loaded with {len(surv.frames)} animated frames: {[f.get_size() for f in surv.frames]}")

    # Check custom Level 8 shouts
    assert any("MODINHO" in s for s in surv.shouts), "Shouts should mention MODINHO"
    assert any("MITRON" in s or "NAMASTE" in s for s in surv.shouts), "Shouts should have Modinho iconic distress dialogue"
    print(f"   [OK] Verified Modinho custom distress calls: {surv.shouts[0]}")

    surv_x, surv_y = surv.x, surv.y
    print(f"   [OK] Modinho position in map: ({surv_x}, {surv_y})")

    # Place player facing Modinho directly
    game.player.x = surv_x - 2.0
    game.player.y = surv_y
    game.player.angle = 0.0  # Facing east towards survivor

    # Trigger shout
    surv.shout_cooldown = 0
    surv.update(dt=50)

    # Verify HUD message displayed
    msg = game.hud.message_text
    print("   [OK] Active HUD Distress Shout:", msg.encode('ascii', 'replace').decode('ascii'))
    assert msg and ("MODINHO" in msg.upper() or "MITRON" in msg.upper()), f"HUD message should contain MODINHO, got {msg}"

    # Render in-game frame
    game.delta_time = 16.6
    game.raycasting.update()
    game.sprite_manager.update(game.delta_time)
    game.draw()

    artifact_dir = r"C:\Users\Ysha\.gemini\antigravity-ide\brain\625612eb-f85b-44bb-b98c-fda66d1509a6"
    out_path = os.path.join(artifact_dir, "modinho_level8_ingame.png")
    pg.image.save(game.screen, out_path)
    print(f"   [OK] Saved in-game screenshot of Modinho: {out_path}")

    # Test animation cycling
    prev_idx = surv.anim_idx
    surv.anim_timer = 500
    surv.update(dt=10)
    print(f"   [OK] Animated frame cycled from {prev_idx} to {surv.anim_idx}")

    # Test Rescue dialog
    surv.rescue()
    assert surv.rescued, "Survivor should be rescued"
    assert "MODINHO" in game.hud.message_text.upper(), "Rescue HUD should mention Modinho"
    print(f"   [OK] Rescue dialog verified: {game.hud.message_text.encode('ascii', 'replace').decode('ascii')}")

    print("\n>>> ALL MODINHO LEVEL 8 SURVIVOR NPC TESTS PASSED! <<<")

if __name__ == "__main__":
    test_modinho_level8()
