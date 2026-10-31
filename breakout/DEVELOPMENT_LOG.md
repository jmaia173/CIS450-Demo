# Development Log - Breakout

Joao Maia
2026.10.30

## First Prompt

Read `AGENTS.md`, `SPEC.md`, and `LICENSE` before beginning.

Implement the Breakout game described in `SPEC.md`, following the instructions in `AGENTS.md` and the licensing requirements in `LICENSE`.

Create all necessary application files, including `index.html` and any CSS or JavaScript files you need. Keep the implementation simple and do not introduce external dependencies.

After implementation, summarize the files you created, explain how to run the game, and describe how to test it against the requirements in `SPEC.md`. Be honest about any tests you have not actually performed.


## First Test

1. The game opens in a browser without installation or build steps: PASS 
2. The player can start the game and move the paddle with the keyboard: PASS 
3. The paddle remains inside the game boundaries: PASS 
4. The ball bounces off the walls and paddle: PASS 
5. Bricks disappear when hit, and the score increases correctly: PASS
6. Missing the paddle causes the ball to reset without breaking the game: PASS 
7. The game ends after a missed ball: PASS 
8. Destroying all bricks produces a win state: PASS 
9. The player can restart and play a fresh game: PASS 
10. No external dependencies are required: PASS 


## First Test Notes

During testing, the Restart Game button did not work while the game was in progress. GitHub Copilot fixed it so the button now restarts the game during active play.


## Spec Update

Modified `SPEC.md` to look more like the classic Breakout:
- Changed from 3 rows of royal blue bricks to 5 rows (red, orange, yellow, green, blue from top to bottom), 10 bricks per row.
- Added a half-brick gap on the left and right sides of the formation, replacing the "no gaps" requirement.
- Added 3 lives. Losing a ball keeps the score and bricks, and the game is over only after the third miss.
- Added a lives display and a requirement that the restart button works during active play.
- Removed requirements that conflicted with these changes (royal blue bricks, no side gaps, game over after one miss).


## Second Prompt

Read `AGENTS.md`, `SPEC.md`, and `LICENSE` before beginning.

`SPEC.md` has been updated. Modify the existing Breakout game so it matches the revised `SPEC.md`, following `AGENTS.md` and the licensing requirements in `LICENSE`. Preserve working behavior that the spec does not change, and avoid rewriting unrelated code.

If any requirements in `SPEC.md` conflict, tell me and explain how you interpreted them.

After the changes, summarize which files you modified, explain how to run the game, and describe how to test it against `SPEC.md`. Be honest about any tests you have not actually performed.


## Second Test

1. Five rows of bricks, colored red, orange, yellow, green, blue from top to bottom: PASS
2. Half-brick gap on the left and right sides of the formation: PASS
3. Lives display starts at 3: PASS
4. Paddle moves with arrow keys, stops on release, and stays inside the boundaries: PASS
5. Ball bounces off the walls and paddle: PASS
6. Bricks disappear when hit and the score increases by 1: PASS
7. Missing the ball costs one life and keeps the score and remaining bricks: PASS
8. Ball and paddle reset and wait for launch after a nonfatal miss: PASS
9. Game Over appears after the third miss and the ball stops: PASS
10. Restart during active play returns to the ready state with score 0 and 3 lives: PASS
11. Restart after Game Over starts a fresh game with all 50 bricks: PASS
12. Clearing all 50 bricks shows the win state: PASS