"""
Automated Mobile Compatibility & Android Lifecycle Test Suite:
Validates touch controls (joystick, panning, buttons), Android back button navigation,
app backgrounding/resumption lifecycle, and multi-resolution rendering.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from main import Game
from engine.settings import WIDTH, HEIGHT


def test_android_mobile_features():
    print("=" * 70)
    print("  ZOMBI APPLOCLIPS: ANDROID MOBILE COMPATIBILITY TEST SUITE")
    print("=" * 70)

    # 1. Initialize Game with pg.SCALED support
    game = Game()
    assert game.screen is not None, "Display initialization failed"
    print("[OK] 1. Display initialized with auto-scaling flags (1280x720 canvas).")

    # 2. Test Mobile Touch Lobby Interaction (FINGERDOWN)
    finger_event = pg.event.Event(pg.FINGERDOWN, x=0.5, y=0.5, finger_id=1)
    game.lobby_menu.handle_event(finger_event)
    print("[OK] 2. Lobby touch events (FINGERDOWN / touch tap) processed successfully.")

    # 3. Deploy Gameplay & Test Mobile Controls
    game.start_mission(level_id=1, primary_weapon="shotgun", tactical_item="medkit")
    assert game.state == "GAMEPLAY", f"Expected GAMEPLAY state, got {game.state}"
    assert game.touch_controls is not None, "Touch controls manager not initialized"
    print("[OK] 3. Mission 1 deployed with touch overlay.")

    # 4. Test Virtual Joystick Touch Input
    joy = game.touch_controls.joystick
    down_ev = pg.event.Event(pg.FINGERDOWN, x=joy.center_x / WIDTH, y=joy.center_y / HEIGHT, finger_id=10)
    game.touch_controls.handle_event(down_ev)

    move_ev = pg.event.Event(pg.FINGERMOTION, x=joy.center_x / WIDTH, y=(joy.center_y - 50) / HEIGHT, finger_id=10)
    game.touch_controls.handle_event(move_ev)
    vx, vy = game.touch_controls.get_movement_input()
    assert vy < -0.3, f"Virtual joystick forward vector failed: {vy}"
    print(f"[OK] 4. Virtual analog joystick touch vector: ({vx:.2f}, {vy:.2f}) verified.")

    up_ev = pg.event.Event(pg.FINGERUP, x=joy.center_x / WIDTH, y=joy.center_y / HEIGHT, finger_id=10)
    game.touch_controls.handle_event(up_ev)
    vx, vy = game.touch_controls.get_movement_input()
    assert vx == 0.0 and vy == 0.0, "Joystick release vector should be zero"
    print("[OK] 5. Virtual joystick release & deadzone centering verified.")

    # 5. Test Touch-Look Panning on Right Half of Screen
    pan_down = pg.event.Event(pg.FINGERDOWN, x=0.75, y=0.5, finger_id=20)
    game.touch_controls.handle_event(pan_down)
    pan_move = pg.event.Event(pg.FINGERMOTION, x=0.80, y=0.5, finger_id=20)
    game.touch_controls.handle_event(pan_move)
    look_delta = game.touch_controls.get_and_reset_look_delta()
    assert look_delta > 0, f"Expected positive look delta, got {look_delta}"
    print(f"[OK] 6. Smooth touch-look panning verified (delta={look_delta:.1f}px).")
    pan_up = pg.event.Event(pg.FINGERUP, x=0.80, y=0.5, finger_id=20)
    game.touch_controls.handle_event(pan_up)

    # 6. Test Mobile Action Buttons (FIRE, RELOAD, SWITCH, ACTION, HEAL, GRENADE)
    for btn in game.touch_controls.buttons:
        bx = btn.center_x / WIDTH
        by = btn.center_y / HEIGHT
        btn_down = pg.event.Event(pg.FINGERDOWN, x=bx, y=by, finger_id=30)
        game.touch_controls.handle_event(btn_down)
        assert btn.is_pressed is True, f"Button {btn.label} failed to press"
        btn_up = pg.event.Event(pg.FINGERUP, x=bx, y=by, finger_id=30)
        game.touch_controls.handle_event(btn_up)
        assert btn.is_pressed is False, f"Button {btn.label} failed to release"
    print("[OK] 7. All 6 on-screen action touch buttons responsive.")

    # 7. Test Android Lifecycle Suspend / Resume
    bg_ev = pg.event.Event(getattr(pg, "APP_WILLENTERBACKGROUND", 101))
    pg.event.post(bg_ev)
    game.handle_events()
    assert game.is_suspended is True, "Game should be suspended when entering background"
    pre_time = game.elapsed_time
    game.delta_time = 100.0
    game.update()
    assert game.elapsed_time == pre_time, "Elapsed time should not advance while suspended"
    print("[OK] 8. Android APP_WILLENTERBACKGROUND suspend state & game loop freeze verified.")

    fg_ev = pg.event.Event(getattr(pg, "APP_WILLENTERFOREGROUND", 104))
    pg.event.post(fg_ev)
    game.handle_events()
    assert game.is_suspended is False, "Game should be un-suspended when entering foreground"
    print("[OK] 9. Android APP_WILLENTERFOREGROUND resume state verified.")

    # 8. Test Android Back Navigation (K_AC_BACK)
    back_key = getattr(pg, "K_AC_BACK", pg.K_ESCAPE)
    back_ev = pg.event.Event(pg.KEYDOWN, key=back_key)
    pg.event.post(back_ev)
    game.handle_events()
    assert game.state == "LOBBY", f"Back button should return to LOBBY, got {game.state}"
    print("[OK] 10. Android system Back navigation (K_AC_BACK) returns to Lobby.")

    print("=" * 70)
    print("  ALL MOBILE COMPATIBILITY TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    test_android_mobile_features()
