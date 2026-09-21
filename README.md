# CIS450-demo

## Introduction

This repo illustrates best practice README file generation.

## Projects

OpenCV image processing demos.

### Edge Detection

This project demonstrates edge detection using OpenCV. Edge detection converts a color image into a line drawing by finding locations where the brightness changes rapidly.

The program first converts each color image to grayscale. It then uses Gaussian blur to reduce noise and Sobel operators to calculate the changes in the image in the X and Y directions. The gradient magnitude is then thresholded to create the edges.

The edge image is then blended with the original color image. The `blend` setting controls how much of the edge image is mixed with the original image. The `thresh` setting controls which edges are included, and the `blur` setting controls how much the image is smoothed before edge detection.

### Images

The original images are stored in the `W5A-Images` directory. The resulting edge images are saved in the `edges` directory using the `.edges.jpg` suffix.

## Edge Detection Settings

| Image | Blend | Threshold | Blur |
|---|---:|---:|---:|
| art.png | 46 | 79 | 15 |
| frog.png | 41 | 76 | 7 |
| map.png | 18 | 2 | 7 |
| pokemon.png | 48 | 75 | 9 |
| sunset.png | 25 | 57 | 3 |

## Resources

<img src="opencv-logo.png" alt="OpenCV logo" width="150" />

[OpenCV](https://opencv.org/)