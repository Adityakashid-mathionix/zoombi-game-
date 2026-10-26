import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

from main import Game

def test_movement_all_levels():
    print(">>> Testing Smooth Movement across Levels 2 through 8 <<<")
    game = Game()

    for lvl_id in range(2, 9):
        game.start_mission(level_id=lvl_id, random_map=False)
        p = game.player
        start_x, start_y = p.x, p.y

        # Simulate pressing forward (W) for 15 frames (250 ms)
        for _ in range(15):
            game.delta_time = 16.6
            p.angle = 0.0  # Facing east (toward open hallway)
            base_speed = 0.004 * game.delta_time
            p.check_wall_collision(base_speed, 0.0)

        moved_dist = abs(p.x - start_x)
        assert moved_dist > 0.3, f"Level {lvl_id}: Player failed to move! Moved distance: {moved_dist}"
        print(f"   [OK] Level {lvl_id}: Player started at ({start_x}, {start_y}) and moved smoothly to ({p.x:.2f}, {p.y:.2f}) [dist={moved_dist:.2f}]")

    print("\n>>> ALL LEVELS 2-8 MOVEMENT TESTS PASSED! <<<")

if __name__ == "__main__":
    test_movement_all_levels()
