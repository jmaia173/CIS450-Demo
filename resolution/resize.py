import cv2 as cv
import os

PHOTOS_DIR = "photos"
OUTPUT_DIR = "resolution"
TARGET_WIDTH = 640

# Collect all image files under photos/ (including subfolders like panorama1, panorama2)
image_paths = []
for root, dirs, files in os.walk(PHOTOS_DIR):
    for f in files:
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            image_paths.append(os.path.join(root, f))

if not image_paths:
    print("No images found in", PHOTOS_DIR)

for path in image_paths:
    img = cv.imread(path)

    if img is None:
        print(f"Could not read {path}, skipping.")
        continue

    height, width = img.shape[:2]

    # Compute new height that preserves the aspect ratio, rounded to nearest int
    ratio = width / TARGET_WIDTH
    new_height = round(height / ratio)

    resized_image = cv.resize(
        img,
        (TARGET_WIDTH, new_height),
        interpolation=cv.INTER_LINEAR
    )

    # Build output filename: originalname-640xVVV.png
    base_name = os.path.splitext(os.path.basename(path))[0]
    output_filename = f"{base_name}-640x{new_height}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    cv.imwrite(output_path, resized_image)
    print(f"Saved {output_path}  ({TARGET_WIDTH}x{new_height})")

print("Done.")