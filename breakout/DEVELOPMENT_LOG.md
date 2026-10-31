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