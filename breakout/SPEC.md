# Breakout Game — Specification

## 1. Objective

Create a playable, browser-based version of the classic Atari Breakout arcade game.

The player controls a paddle at the bottom of the game area to bounce a ball into a formation of bricks. The goal is to destroy all the bricks before losing all three lives.

## 2. Technical Requirements

- The game must run in a modern desktop web browser.
- The game must use HTML, CSS, and JavaScript.
- Do not use external libraries, frameworks, or services.
- The game must run locally by opening `index.html` in a browser. No server or build process should be required.
- Organize the code into files as appropriate for a small project.

## 3. Game Display and Layout

- The game must have a clearly defined rectangular playing area.
- The playing area must contain a paddle at the bottom, a ball, and five rows of bricks near the top, with ten bricks in each row (50 bricks total).
- The rows must be colored from top to bottom: red (#FF0000), orange (#FFA500), yellow (#FFFF00), green (#008000), blue (#0000FF).
- The brick formation must be horizontally centered, with a gap equal to exactly one half brick width between the formation and the left boundary, and between the formation and the right boundary.
- The game boundaries must prevent the ball from escaping the playing area. The ball must bounce off the left, right, and top boundaries.
- Display the player's score, the number of remaining lives, and instructions for starting and controlling the game.
- Display an appropriate message when the player wins or loses.

## 4. Paddle Controls

- The player must be able to move the paddle left and right using the keyboard left and right arrow keys.
- The paddle must not move outside the left or right boundaries of the game area.
- Paddle movement must stop when the player releases the corresponding key.

## 5. Ball Behavior

- The ball must move continuously once a game begins.
- The ball must bounce off the top, left, and right walls.
- The ball must bounce off the paddle when it collides with it.
- The ball must destroy a brick when it collides with that brick.
- The ball must not pass through walls, the paddle, or bricks under normal play.
- When the ball collides with a brick, the brick disappears and the ball bounces away from the brick.
- The ball's direction must change based on the surface it hits: a collision with the top or bottom of a brick reverses its vertical direction, while a collision with the left or right side reverses its horizontal direction.

## 6. Bricks and Scoring

- Display a formation of multiple bricks.
- When the ball hits a brick, that brick must disappear.
- The player's score must increase by one point when a brick is destroyed.
- A destroyed brick must not award points again.
- The game is won when all bricks have been destroyed.

## 7. Lives and Losing the Game

- The player starts each game with 3 lives.
- If the ball passes below the paddle, the player loses one life.
- After losing a life with lives remaining, the ball and paddle return to their starting positions and wait for the player to launch again. The score and the remaining bricks must not change.
- When the last life is lost, the game is lost. The ball must stop moving and a clear "Game Over" message must be displayed.
- Provide a way to restart the game.
- Restarting must reset the score, restore all bricks, restore lives to 3, and return the ball and paddle to their starting positions.

## 8. Game States and Restart

- The game must have a clear initial state before play begins.
- The player must be able to start the game.
- The game must distinguish between ready, active play, waiting to launch after a lost life, a win, and a loss.
- When the game is won or lost, active gameplay must stop.
- The player must be able to restart the game and play again from the beginning, including during active play.
- Pressing the restart button during active play must immediately return the game to the initial ready state and wait for the player to start again.
- Restarting must reset the score, bricks, lives, ball, and paddle to their initial states.

## 9. Acceptance Criteria

The implementation is complete when all of the following can be verified:

1. The game opens in a browser without installation or build steps.
2. The player can start the game and move the paddle with the keyboard.
3. The paddle remains inside the game boundaries.
4. The ball bounces off the walls and paddle.
5. Bricks disappear when hit, and the score increases correctly.
6. Missing the paddle costs one life and resets the ball and paddle, while keeping the score and remaining bricks.
7. The game ends after the third missed ball.
8. Destroying all bricks produces a win state.
9. The player can restart after a win, a loss, or during play and start a fresh game with 3 lives.
10. No external dependencies are required.
11. The game shows five rows of bricks (red, orange, yellow, green, blue from top to bottom) with a half-brick gap on the left and right sides.
12. The number of remaining lives is displayed and starts at 3.

## 10. Scope

- Keep the game simple and focus on correct, reliable gameplay.
- The following features are not required: sound effects, power-ups, multiple levels, high-score storage, animations beyond basic gameplay, mobile touch controls, or online leaderboards.