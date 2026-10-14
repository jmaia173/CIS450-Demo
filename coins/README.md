# OpenCV Automated Coin Detection & Classification

An iterative computer vision project built using Python and OpenCV to detect U.S. coins, classify them by denomination using HSV color analysis and relative sizes, and calculate total monetary values. 

This document details both the computer vision pipeline and the development process across multiple iterations and AI debug sessions.

---

## Program Architecture & Pipeline

The script (`findcoins.py`) processes images through the following steps:

1. **Load Image**: Loads input via `cv2.imread()` and creates a working copy for annotations.
2. **Grayscale Conversion**: Converts frames to single-channel grayscale (`cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)`) for edge detection.
3. **Gaussian Blur**: Filters noise (`cv2.GaussianBlur()`) to prevent spurious edge detection.
4. **Hough Circle Detection**: Uses `cv2.HoughCircles()` with `cv2.HOUGH_GRADIENT` to locate circular shapes based on tuned parameters (`dp`, `minDist`, `param1`, `param2`, `minRadius`, `maxRadius`).
5. **Penny Identification (HSV & Circular Masking)**:
   - Converts cropped coin regions into HSV color space (`cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)`).
   - Applies a **circular mask** matching the detected center and radius to isolate internal coin pixels and ignore surrounding background colors.
   - Identifies pennies based on copper/red color ranges.
6. **Silver Coin Classification (Relative Radii)**:
   - Classifies non-pennies (dimes, nickels, quarters) by comparing their detected circle radii against physical scale proportions rather than fixed pixel dimensions:
     - **Dime**: ~17.91 mm
     - **Nickel**: ~21.21 mm
     - **Quarter**: ~24.26 mm
7. **Annotation & Valuation**:
   - Outlines coins and labels denominations using specific BGR colors:
     - **Pennies** ($0.01): Red
     - **Nickels** ($0.05): Green
     - **Dimes** ($0.10): Blue
     - **Quarters** ($0.25): Yellow
   - Sums monetary totals and overlays the final value onto the image.
8. **Export**: Saves output as `<filename>.annotated.png` without overwriting the original file.

---

## AI Debugging & Iteration History

### Conversation 1 & 2: Initial Hough Threshold Tuning
* **Problem**: Low `param2` and small `minDist` settings led to duplicate detections and false circles.
* **Changes**: Increased thresholds (`minDist = 120`, `param2 = 55`) and introduced image-specific configuration.
* **Result**: Reduced false circles in sparse images, though strict parameters caused missed detections in dense images (Image 4).

### Conversation 3: Misclassifications & Dense Image Challenges
* **Problem**: Misassigned coin colors in Images 2 and 3; dense cluster in Image 4 caused missing detections.
* **Changes**: Refined HSV copper ranges, modified Gaussian blur, introduced relative coin sizing, and implemented per-image Hough parameter sets.

### Conversation 4: Attempted Contour & Thresholding Approach
* **Problem**: Strict Hough settings caused coins to disappear.
* **Exploration**: Tested `cv2.adaptiveThreshold()` and `cv2.minEnclosingCircle()` to find coin regions via contours.
* **Result**: Explored as an alternative, but Hough Circle detection ultimately yielded better results for this dataset.

### Conversation 5: Relative Size Classification
* **Problem**: Fixed pixel radius thresholds failed across images with varying camera scales.
* **Solution**: Adopted a two-part classification logic: isolate pennies by copper color, then classify remaining coins using relative U.S. coin diameter ratios (Dime: 17.91mm, Nickel: 21.21mm, Quarter: 24.26mm).

### Conversation 6: Image 3 Penny Background Bleed
* **Problem**: A silver coin on a reddish/brown background was incorrectly classified as a penny because the `is_penny()` function analyzed a rectangular bounding box.
* **Solution**: Replaced rectangular cropping with a circular mask on the detected coin coordinates, forcing color evaluation to focus exclusively on internal surface pixels.

### Conversation 7: Image 4 Dense Coin Cluster
* **Problem**: Global Hough settings failed to detect closely packed coins in Image 4.
* **Solution**: Configured per-image parameters. Image 4 uses a lower accumulator threshold (`param2`) and smaller `minDist` to catch clustered coins.

---

## Current Results & Limitations

* **Improvements**: Reduced false detections, accurate HSV penny masking, relative silver coin sizing, per-image Hough configurations, and annotated outputs with calculated total values.
* **Limitations**: The parameters are tuned for the assignment's four target images rather than functioning as a universal coin detector. Edge cases remain in highly dense clusters (Image 4) and complex background environments (Image 3).

---

## Lessons Learned

The primary takeaway from this project is that AI-generated code is not guaranteed to be functionally correct simply because it executes without errors. Human evaluation of spatial outputs was essential to identify issues like false circles, background color bleeding, and missed detections. 

Successful implementation required a human/AI development loop:
`Human Specification ──► AI Code Generation ──► Human Output Evaluation ──► AI Revision ──► Testing`