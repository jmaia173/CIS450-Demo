# Prototype

Proof-of-concept script from the design phase. It detects faces with an OpenCV
Haar cascade, blurs them, and prints a photo's EXIF metadata including GPS.

Usage: `pip install -r requirements.txt` then `python prototype.py photo.jpg`

Findings: a fixed blur left faces recognizable, so the final app scales blur
strength to face size and adds pixelate and black box options. OpenCV 5 dropped
the Haar `CascadeClassifier`, so OpenCV is pinned below version 5.
