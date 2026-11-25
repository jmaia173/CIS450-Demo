"""Prototype: detect faces and blur them, then print EXIF metadata (incl. GPS)."""
import sys
import cv2
from PIL import Image, ExifTags

path = sys.argv[1]

# Face detection with OpenCV's built-in Haar cascade
img = cv2.imread(path)
if img is None:
    sys.exit("Could not read image (HEIC is not supported, convert to JPG first)")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
print(f"Faces found: {len(faces)}")

# Blur each detected face region
for (x, y, w, h) in faces:
    roi = img[y:y + h, x:x + w]
    img[y:y + h, x:x + w] = cv2.GaussianBlur(roi, (51, 51), 0)
cv2.imwrite("blurred.jpg", img)

# Read EXIF metadata
exif = Image.open(path).getexif()
for tag_id, value in exif.items():
    print(ExifTags.TAGS.get(tag_id, tag_id), ":", value)
gps = exif.get_ifd(0x8825)  # GPS section
print("GPS:", dict(gps) if gps else "none")
