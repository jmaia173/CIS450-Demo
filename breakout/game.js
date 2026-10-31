"use strict";

const canvas = document.querySelector("#game");
const context = canvas.getContext("2d");
const scoreDisplay = document.querySelector("#score");
const livesDisplay = document.querySelector("#lives");
const statusDisplay = document.querySelector("#status");
const startButton = document.querySelector("#start-button");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;
const paddle = { width: 112, height: 12, x: (WIDTH - 112) / 2, y: HEIGHT - 36, speed: 440 };
const ball = { radius: 8, x: WIDTH / 2, y: HEIGHT - 58, speedX: 210, speedY: -300 };
const keys = { left: false, right: false };
const brickRows = 5;
const brickColumns = 10;
const brickHeight = 22;
const brickGap = 4;
const brickTop = 54;
const brickColors = ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF"];
const bricks = [];

let score = 0;
let lives = 3;
let gameState = "ready";
let previousFrameTime = 0;

function resetBricks() {
  bricks.length = 0;
  const brickWidth = (WIDTH - brickGap * (brickColumns - 1)) / (brickColumns + 1);
  const sideMargin = brickWidth / 2;

  for (let row = 0; row < brickRows; row += 1) {
    for (let column = 0; column < brickColumns; column += 1) {
      bricks.push({
        x: sideMargin + column * (brickWidth + brickGap),
        y: brickTop + row * (brickHeight + brickGap),
        width: brickWidth,
        height: brickHeight,
        color: brickColors[row]
      });
    }
  }
}

function resetBallAndPaddle() {
  paddle.x = (WIDTH - paddle.width) / 2;
  ball.x = WIDTH / 2;
  ball.y = HEIGHT - 58;
  ball.speedX = 210;
  ball.speedY = -300;
}

function resetGame() {
  score = 0;
  lives = 3;
  scoreDisplay.textContent = String(score);
  livesDisplay.textContent = String(lives);
  keys.left = false;
  keys.right = false;
  resetBricks();
  resetBallAndPaddle();
  gameState = "ready";
  statusDisplay.textContent = "Press Start Game or Space to launch the ball.";
  startButton.textContent = "Start Game";
  draw();
}

function startGame() {
  if (gameState !== "ready" && gameState !== "waiting") return;

  gameState = "playing";
  statusDisplay.textContent = "Game in progress. Keep the ball above the paddle!";
  startButton.textContent = "Restart Game";
}

function finishGame(state) {
  gameState = state;

  if (state === "won") {
    statusDisplay.textContent = "You Win! All bricks have been cleared.";
  } else {
    statusDisplay.textContent = "Game Over. Press Restart Game to play again.";
  }
}

function drawBricks() {
  for (const brick of bricks) {
    context.fillStyle = brick.color;
    context.fillRect(brick.x, brick.y, brick.width, brick.height);
  }
}

function draw() {
  context.clearRect(0, 0, WIDTH, HEIGHT);
  context.fillStyle = "#151d2c";
  context.fillRect(0, 0, WIDTH, HEIGHT);
  drawBricks();

  context.fillStyle = "#f3f5fb";
  context.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);

  context.beginPath();
  context.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
  context.fillStyle = "#f5c96b";
  context.fill();

  if (gameState !== "playing") {
    const messages = {
      ready: "PRESS START OR SPACE",
      waiting: "PRESS SPACE TO LAUNCH",
      won: "YOU WIN!",
      lost: "GAME OVER"
    };
    context.fillStyle = "#101522cc";
    context.fillRect(0, HEIGHT / 2 - 30, WIDTH, 60);
    context.fillStyle = "#ffffff";
    context.font = "700 22px system-ui, sans-serif";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(messages[gameState], WIDTH / 2, HEIGHT / 2);
  }
}

function movePaddle(deltaTime) {
  if (keys.left) paddle.x -= paddle.speed * deltaTime;
  if (keys.right) paddle.x += paddle.speed * deltaTime;
  paddle.x = Math.max(0, Math.min(WIDTH - paddle.width, paddle.x));
}

function collideWithBricks(previousX, previousY) {
  for (let index = 0; index < bricks.length; index += 1) {
    const brick = bricks[index];
    const closestX = Math.max(brick.x, Math.min(ball.x, brick.x + brick.width));
    const closestY = Math.max(brick.y, Math.min(ball.y, brick.y + brick.height));
    const distanceX = ball.x - closestX;
    const distanceY = ball.y - closestY;

    if (distanceX * distanceX + distanceY * distanceY > ball.radius * ball.radius) continue;

    const cameFromSide = previousX + ball.radius <= brick.x
      || previousX - ball.radius >= brick.x + brick.width;
    const cameFromTopOrBottom = previousY + ball.radius <= brick.y
      || previousY - ball.radius >= brick.y + brick.height;

    if (cameFromSide && !cameFromTopOrBottom) {
      ball.speedX *= -1;
      ball.x = previousX < brick.x ? brick.x - ball.radius : brick.x + brick.width + ball.radius;
    } else if (cameFromTopOrBottom && !cameFromSide) {
      ball.speedY *= -1;
      ball.y = previousY < brick.y ? brick.y - ball.radius : brick.y + brick.height + ball.radius;
    } else {
      const overlapX = ball.radius + brick.width / 2
        - Math.abs(ball.x - (brick.x + brick.width / 2));
      const overlapY = ball.radius + brick.height / 2
        - Math.abs(ball.y - (brick.y + brick.height / 2));

      if (overlapX < overlapY) {
        ball.speedX *= -1;
        ball.x += ball.x < brick.x + brick.width / 2 ? -overlapX : overlapX;
      } else {
        ball.speedY *= -1;
        ball.y += ball.y < brick.y + brick.height / 2 ? -overlapY : overlapY;
      }
    }

    bricks.splice(index, 1);
    score += 1;
    scoreDisplay.textContent = String(score);
    if (bricks.length === 0) finishGame("won");
    return;
  }
}

function update(deltaTime) {
  movePaddle(deltaTime);

  const previousX = ball.x;
  const previousY = ball.y;
  ball.x += ball.speedX * deltaTime;
  ball.y += ball.speedY * deltaTime;

  if (ball.x - ball.radius < 0) {
    ball.x = ball.radius;
    ball.speedX = Math.abs(ball.speedX);
  } else if (ball.x + ball.radius > WIDTH) {
    ball.x = WIDTH - ball.radius;
    ball.speedX = -Math.abs(ball.speedX);
  }

  if (ball.y - ball.radius < 0) {
    ball.y = ball.radius;
    ball.speedY = Math.abs(ball.speedY);
  }

  collideWithBricks(previousX, previousY);
  if (gameState !== "playing") return;

  if (
    ball.speedY > 0
    && previousY + ball.radius <= paddle.y
    && ball.y + ball.radius >= paddle.y
    && ball.x + ball.radius >= paddle.x
    && ball.x - ball.radius <= paddle.x + paddle.width
  ) {
    const hitPosition = (ball.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2);
    ball.y = paddle.y - ball.radius;
    ball.speedX = hitPosition * 300;
    ball.speedY = -Math.sqrt(330 * 330 - ball.speedX * ball.speedX);
  }

  if (ball.y - ball.radius > paddle.y + paddle.height) loseLife();
}

function loseLife() {
  lives -= 1;
  livesDisplay.textContent = String(lives);

  if (lives === 0) {
    finishGame("lost");
    return;
  }

  resetBallAndPaddle();
  gameState = "waiting";
  statusDisplay.textContent = `Life lost. ${lives} ${lives === 1 ? "life" : "lives"} left. Press Space or Launch Ball to continue.`;
  startButton.textContent = "Launch Ball";
}

function frame(timestamp) {
  const deltaTime = previousFrameTime
    ? Math.min((timestamp - previousFrameTime) / 1000, 1 / 30)
    : 0;
  previousFrameTime = timestamp;

  if (gameState === "playing") update(deltaTime);
  draw();
  window.requestAnimationFrame(frame);
}

function handleKey(event, isPressed) {
  if (event.key === "ArrowLeft" || event.key === "ArrowRight" || event.code === "Space") {
    event.preventDefault();
  }

  if (event.key === "ArrowLeft") keys.left = isPressed;
  if (event.key === "ArrowRight") keys.right = isPressed;
  if (isPressed && (event.code === "Space" || event.key === "Enter")) {
    startGame();
  }
}

window.addEventListener("keydown", (event) => handleKey(event, true));
window.addEventListener("keyup", (event) => handleKey(event, false));
window.addEventListener("blur", () => {
  keys.left = false;
  keys.right = false;
});
startButton.addEventListener("click", (event) => {
  if (gameState === "ready" || gameState === "waiting") {
    startGame();
  } else {
    resetGame();
  }
  event.currentTarget.blur();
});

resetBricks();
resetBallAndPaddle();
scoreDisplay.textContent = String(score);
livesDisplay.textContent = String(lives);
draw();
window.requestAnimationFrame(frame);
