# Final Project

## Description
PrivacyShield is a web app for sharing photos safely. Users upload an image, and it automatically detects faces and blurs, pixelates, or blacks them out. Users can also draw boxes to hide anything else, such as license plates or documents. The app reads hidden EXIF metadata like GPS location and camera details, shows what the photo exposes, and returns a cleaned download.

## Design

### Approach
I am building PrivacyShield on top of the provided Flask and Docker template, keeping its structure: a web page served on the port from the `PORT` environment variable, a root route `/`, and OpenCV for the image processing. The app has three parts. First, face detection uses OpenCV's built-in Haar cascade classifier, and each detected region can be blurred, pixelated, or covered with a black box. Second, users can draw their own boxes on the preview to hide anything the detector misses, such as license plates. Third, the Pillow library reads EXIF metadata, and the app reports what the photo reveals (especially GPS location) and returns a cleaned copy without any metadata.

The free Render tier limits the app to 512 MB of RAM and 0.1 CPU, so I chose lightweight methods and designed around those limits. Haar cascades are much cheaper than a neural network. Uploads are resized to at most 1600 pixels on the long edge before processing. Images are processed in memory and never saved to disk, which avoids the template's shared `static/original.jpg` problem and fits a privacy tool that should not keep user photos. I decided not to promise automatic license plate detection because OpenCV's built-in plate cascade is trained on Russian plates, so manual boxes are the more reliable option.

### Prototype findings
I wrote a small prototype script that detects faces with an OpenCV Haar cascade, blurs them, and prints a photo's EXIF metadata including GPS. While setting it up I found that OpenCV 5 no longer includes the Haar `CascadeClassifier` in its main package, so I pinned `opencv-python-headless<5` for the project and used a clean virtual environment. I tested it on 4 of my own photos, and the detector found and blurred the faces in all of them. However, the fixed blur strength I used left faces partly recognizable. Because of this, the final app will scale the blur strength to the size of each face and offer pixelate and black box options, which hide a face more securely than blur. I also noticed that iPhone photos are HEIC files, which OpenCV cannot read, so I converted them to JPG for testing and plan to add HEIC support with the `pillow-heif` package if time allows.

### Web links used
- OpenCV Cascade Classifier tutorial: https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html
- Pillow `Image.getexif` documentation: https://pillow.readthedocs.io/en/stable/reference/Image.html
- Render free tier limits: https://render.com/docs/free
- Flask documentation: https://flask.palletsprojects.com/

### AI usage
I used the Claude chatbot (Anthropic). I asked it to suggest project ideas that are useful in the real world and fit Render's free tier, and I chose PrivacyShield from its suggestions. I also asked it to help me write a prototype script for face detection and EXIF reading and a design plan that fits the 512 MB RAM limit. When the prototype failed with a missing `CascadeClassifier` error, I used it to troubleshoot, which led me to the OpenCV version problem. I will keep updating this section as I implement and test the project.