import cv2
import numpy as np
import os
import sys

# Colors are BGR because OpenCV uses BGR
COLORS = {
    "penny": (0, 0, 255),      # Red
    "nickel": (0, 255, 0),     # Green
    "dime": (255, 0, 0),       # Blue
    "quarter": (0, 255, 255)   # Yellow
}

VALUES = {
    "penny": 0.01,
    "nickel": 0.05,
    "dime": 0.10,
    "quarter": 0.25
}


def is_penny(crop):
    """
    Determine whether a coin is a penny based on its
    copper/orange color.
    """
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    # Copper/red/orange colors
    lower1 = np.array([0, 40, 40])
    upper1 = np.array([18, 255, 255])

    lower2 = np.array([165, 40, 40])
    upper2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)

    mask = mask1 | mask2

    copper_ratio = np.mean(mask > 0)

    return copper_ratio > 0.18


def get_coin_crop(image, x, y, r):
    """Safely crop the area surrounding a detected coin."""
    height, width = image.shape[:2]

    x1 = max(0, x - r)
    x2 = min(width, x + r)
    y1 = max(0, y - r)
    y2 = min(height, y + r)

    return image[y1:y2, x1:x2]


def classify_silver_coins(coins):
    """
    Classify non-penny coins using their relative radii.

    US coin diameters:
        Dime    = 17.91 mm
        Nickel  = 21.21 mm
        Quarter = 24.26 mm
    """

    if not coins:
        return

    coin_sizes = {
        "dime": 17.91,
        "nickel": 21.21,
        "quarter": 24.26
    }

    # Try different possible scales and find the one that
    # best matches the detected coin sizes.
    best_scale = None
    best_error = float("inf")

    radii = [coin["r"] for coin in coins]

    for radius in radii:
        for denomination, diameter in coin_sizes.items():
            scale = radius / diameter

            error = 0

            for detected_radius in radii:
                expected = []

                for size in coin_sizes.values():
                    expected.append(scale * size)

                smallest_error = min(
                    abs(detected_radius - value)
                    for value in expected
                )

                error += smallest_error

            if error < best_error:
                best_error = error
                best_scale = scale

    # Assign each coin to the closest expected denomination
    for coin in coins:
        best_type = None
        smallest_error = float("inf")

        for denomination, diameter in coin_sizes.items():
            expected_radius = best_scale * diameter
            error = abs(coin["r"] - expected_radius)

            if error < smallest_error:
                smallest_error = error
                best_type = denomination

        coin["type"] = best_type


def process_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        print(f"Could not open {image_path}")
        return

    output = image.copy()

    height, width = image.shape[:2]
    smallest_dimension = min(height, width)

    # Convert to grayscale and blur before Hough detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detect large circular objects.
    #
    # The relatively high param2 is important because it prevents
    # details in the background and on the coins from being detected
    # as separate circles.
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=int(smallest_dimension * 0.09),
        param1=100,
        param2=45,
        minRadius=max(20, int(smallest_dimension * 0.055)),
        maxRadius=int(smallest_dimension * 0.20)
    )

    detected_coins = []

    if circles is not None:

        circles = np.around(circles[0]).astype(int)

        for x, y, r in circles:

            crop = get_coin_crop(image, x, y, r)

            if crop.size == 0:
                continue

            # First identify pennies using their copper color.
            if is_penny(crop):
                detected_coins.append({
                    "x": x,
                    "y": y,
                    "r": r,
                    "type": "penny"
                })
            else:
                # Save silver coins for size-based classification.
                detected_coins.append({
                    "x": x,
                    "y": y,
                    "r": r,
                    "type": None
                })

    # Separate pennies from silver coins
    silver_coins = [
        coin for coin in detected_coins
        if coin["type"] is None
    ]

    # Determine dime/nickel/quarter using relative size
    classify_silver_coins(silver_coins)

    # Count the coins and calculate the total
    counts = {
        "penny": 0,
        "nickel": 0,
        "dime": 0,
        "quarter": 0
    }

    total = 0.0

    for coin in detected_coins:

        coin_type = coin["type"]

        if coin_type not in counts:
            continue

        counts[coin_type] += 1
        total += VALUES[coin_type]

        color = COLORS[coin_type]

        # Draw circle around coin
        cv2.circle(
            output,
            (coin["x"], coin["y"]),
            coin["r"],
            color,
            4
        )

        # Label coin
        label_x = max(5, coin["x"] - coin["r"])
        label_y = max(25, coin["y"] - coin["r"] - 8)

        cv2.putText(
            output,
            coin_type,
            (label_x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2
        )

    # Add a black box for the summary
    cv2.rectangle(
        output,
        (10, 10),
        (230, 150),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        output,
        f"Pennies: {counts['penny']}",
        (20, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        output,
        f"Nickels: {counts['nickel']}",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        output,
        f"Dimes: {counts['dime']}",
        (20, 92),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        output,
        f"Quarters: {counts['quarter']}",
        (20, 119),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        output,
        f"Total: ${total:.2f}",
        (20, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # Save annotated image
    base, _ = os.path.splitext(image_path)
    output_path = f"{base}.annotated.png"

    cv2.imwrite(output_path, output)

    print(
        f"{os.path.basename(image_path)}: "
        f"{len(detected_coins)} coins, "
        f"Total = ${total:.2f}"
    )
    print(f"Saved: {output_path}")


def main():

    # If a specific image is provided:
    # python3 findcoins.py coins1.png
    if len(sys.argv) > 1:
        process_image(sys.argv[1])
        return

    # Otherwise process all four images
    for i in range(1, 5):
        filename = f"coins{i}.png"

        if os.path.exists(filename):
            process_image(filename)
        else:
            print(f"{filename} not found.")


if __name__ == "__main__":
    main()