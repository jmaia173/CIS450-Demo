"""
PrivacyShield - app.py

A small Flask web app for sharing photos safely.

What it does:
  1. Accepts an uploaded photo (JPG, PNG, or HEIC) and shrinks it so it fits
     in the 512 MB of RAM on Render's free tier.
  2. Reads the photo's hidden EXIF metadata (GPS location, camera, owner, dates)
     and reports how much the photo exposes.
  3. Detects faces with an OpenCV Haar cascade and hides each one with a blur,
     a pixelation, or a black box. The blur size scales with the face size.
  4. Returns the protected photo as a download. The download has NO metadata
     because OpenCV writes a brand new JPEG file.

Privacy design: uploads are processed in memory and are never written to disk.

To build:   docker build -t app .
To run:     docker run -p 80:80 app
In browser: http://localhost
(Render sets the PORT environment variable; the app reads it at the bottom.)
"""

import base64
import io
import os
import socket

import cv2
import numpy as np
from flask import Flask, render_template_string, request
from PIL import ExifTags, Image, ImageOps

# HEIC support is optional: iPhone photos are HEIC by default.
try:
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

# ---------------------------------------------------------------------------
# Settings (chosen to fit Render's free tier: 512 MB RAM, 0.1 CPU)
# ---------------------------------------------------------------------------
MAX_SIDE = 1600          # longest edge, in pixels, of the processed photo
DETECT_SIDE = 800        # face detection runs on a smaller copy to save CPU
MAX_UPLOAD_MB = 8        # reject bigger uploads
FACE_PADDING = 0.15      # grow each face box by 15% so hair/chin are covered
MODES = {"blur": "Blur", "pixelate": "Pixelate", "box": "Black box"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 60_000_000  # guards against decompression bombs

hostname = socket.gethostname()

# The face detector is loaded once when the app starts, not on every request.
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
if FACE_CASCADE.empty():
    raise RuntimeError("Could not load the Haar face cascade from OpenCV.")


# ---------------------------------------------------------------------------
# Metadata (EXIF) reading
# ---------------------------------------------------------------------------
def dms_to_degrees(dms, ref):
    """Convert GPS degrees/minutes/seconds plus N/S/E/W into decimal degrees.

    Example: ((45, 31, 12), "N") -> 45.52
    South and West are negative numbers.
    """
    degrees = float(dms[0]) + float(dms[1]) / 60 + float(dms[2]) / 3600
    return -degrees if ref in ("S", "W") else degrees


def clean_value(value):
    """Turn an EXIF value into a short, safe string. Returns None for raw bytes."""
    if isinstance(value, bytes):
        return None
    text = str(value).replace("\x00", "").strip()
    return text[:80] if text else None


def read_metadata(img):
    """Read the EXIF metadata of a PIL image and describe how much it exposes.

    Returns a dict with:
      has_exif  - True if the file contained any EXIF tags
      count     - total number of EXIF tags found
      fields    - list of (label, value) for the interesting tags
      gps       - None, or a dict with latitude, longitude and a map link
      risk      - "High", "Medium", "Low" or "None"
      reasons   - plain-language explanation of the risk level
    """
    exif = img.getexif()
    sub = exif.get_ifd(0x8769)   # camera details (exposure, lens, original date)
    gps_ifd = exif.get_ifd(0x8825)  # GPS location section

    # Section 1: collect the tags a person would care about
    wanted = [
        (exif, 271, "Camera maker"),
        (exif, 272, "Camera model"),
        (exif, 305, "Software"),
        (exif, 306, "Date modified"),
        (exif, 315, "Artist / owner"),
        (sub, 36867, "Date taken"),
        (sub, 42036, "Lens"),
        (sub, 42032, "Camera owner name"),
        (sub, 42033, "Camera serial number"),
    ]
    fields = []
    for source, tag_id, label in wanted:
        value = clean_value(source.get(tag_id)) if tag_id in source else None
        if value:
            fields.append((label, value))

    # Section 2: turn the GPS section into a decimal location
    gps = None
    try:
        if gps_ifd and 2 in gps_ifd and 4 in gps_ifd:
            lat = dms_to_degrees(gps_ifd[2], gps_ifd.get(1, "N"))
            lon = dms_to_degrees(gps_ifd[4], gps_ifd.get(3, "E"))
            gps = {
                "latitude": round(lat, 5),
                "longitude": round(lon, 5),
                "map_url": f"https://www.google.com/maps?q={lat:.5f},{lon:.5f}",
            }
    except (TypeError, ValueError, ZeroDivisionError):
        gps = None  # malformed GPS data: treat as not readable

    # Section 3: decide the risk level
    labels = {label for label, _ in fields}
    identifying = labels & {"Artist / owner", "Camera owner name", "Camera serial number"}
    reasons = []
    if gps:
        risk = "High"
        reasons.append("Shows exactly where the photo was taken.")
    elif identifying:
        risk = "Medium"
        reasons.append("Contains a name or serial number that can identify you or your camera.")
    elif fields:
        risk = "Low"
        reasons.append("Shows the camera model and when the photo was taken.")
    else:
        risk = "None"
        reasons.append("No readable metadata was found in this file.")
    if gps and identifying:
        reasons.append("Also contains a name or serial number.")

    return {
        "has_exif": bool(exif),
        "count": len(exif) + len(sub) + len(gps_ifd),
        "fields": fields,
        "gps": gps,
        "risk": risk,
        "reasons": reasons,
    }


# ---------------------------------------------------------------------------
# Image loading
# ---------------------------------------------------------------------------
def prepare_image(img):
    """Shrink a PIL image to MAX_SIDE, fix its rotation, and return a BGR array.

    JPEG files are decoded at a reduced size (draft mode) to save memory.
    EXIF rotation is applied so photos taken in portrait are not sideways,
    because the cleaned file will no longer carry the rotation tag.
    """
    if img.format == "JPEG":
        img.draft("RGB", (MAX_SIDE, MAX_SIDE))
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    rgb = np.asarray(img)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------------------
# Face detection
# ---------------------------------------------------------------------------
def detect_faces(bgr):
    """Find faces in a BGR image. Returns a list of (x, y, w, h) boxes.

    Detection runs on a copy no larger than DETECT_SIDE pixels (cheaper on the
    0.1 CPU free tier), then the boxes are scaled back to the full-size image.
    """
    height, width = bgr.shape[:2]
    scale = min(1.0, DETECT_SIDE / max(height, width))
    small = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)  # evens out lighting so faces are easier to find

    min_face = max(24, int(min(gray.shape[:2]) * 0.05))
    found = FACE_CASCADE.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(min_face, min_face)
    )
    return [
        (int(x / scale), int(y / scale), int(w / scale), int(h / scale))
        for (x, y, w, h) in found
    ]


def pad_box(box, img_width, img_height):
    """Grow a face box by FACE_PADDING on every side, staying inside the image."""
    x, y, w, h = box
    pad_x, pad_y = int(w * FACE_PADDING), int(h * FACE_PADDING)
    x0, y0 = max(0, x - pad_x), max(0, y - pad_y)
    x1, y1 = min(img_width, x + w + pad_x), min(img_height, y + h + pad_y)
    return x0, y0, x1, y1


# ---------------------------------------------------------------------------
# Hiding faces
# ---------------------------------------------------------------------------
def hide_region(region, mode, strength):
    """Return a hidden version of one image region.

    mode      - "blur", "pixelate" or "box"
    strength  - 1 (light) to 10 (heavy)

    The effect size is based on the region's width, so a big face in a
    high-resolution photo gets a proportionally bigger blur than a small one.
    A Gaussian blur uses a square "kernel" of n x n pixels; here n grows with
    the face width.
    """
    height, width = region.shape[:2]

    if mode == "box":
        return np.zeros_like(region)

    if mode == "pixelate":
        # Fewer, bigger squares at higher strength
        block = max(4, int(width * strength / 25))
        small = cv2.resize(
            region,
            (max(1, width // block), max(1, height // block)),
            interpolation=cv2.INTER_LINEAR,
        )
        return cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)

    # Default: Gaussian blur with a kernel size scaled to the face width
    kernel = max(3, int(width * strength / 10))
    if kernel % 2 == 0:
        kernel += 1  # Gaussian kernels must be odd
    return cv2.GaussianBlur(region, (kernel, kernel), 0)


def protect_faces(bgr, boxes, mode, strength):
    """Return a copy of the image with every box hidden. The original is untouched."""
    out = bgr.copy()
    height, width = out.shape[:2]
    for box in boxes:
        x0, y0, x1, y1 = pad_box(box, width, height)
        out[y0:y1, x0:x1] = hide_region(out[y0:y1, x0:x1], mode, strength)
    return out


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def to_data_uri(bgr, quality):
    """Encode a BGR image as a JPEG data URI that can go straight into an <img> tag.

    OpenCV writes a brand new JPEG, so no EXIF metadata is carried over.
    """
    ok, buffer = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise ValueError("Could not encode the image.")
    encoded = base64.b64encode(buffer.tobytes()).decode("ascii")
    return "data:image/jpeg;base64," + encoded


# ---------------------------------------------------------------------------
# Web page
# ---------------------------------------------------------------------------
PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PrivacyShield</title>
<style>
  :root {
    --navy: #0f2340; --gold: #f2b705; --paper: #eef1f5; --card: #ffffff;
    --ink: #14181f; --muted: #5b6573; --line: #d5dbe3;
    --high: #b3261e; --medium: #a85d00; --low: #2e6b3a; --none: #3b4a5c;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink);
         font: 16px/1.5 "Avenir Next", "Segoe UI", system-ui, sans-serif; }
  main { max-width: 960px; margin: 0 auto; padding: 24px 16px 48px; }
  h1 { margin: 0 0 4px; font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; }
  h1 span { background: var(--navy); color: #fff; padding: 0 .35em; border-radius: 3px; }
  .tagline { margin: 0 0 20px; color: var(--muted); max-width: 60ch; }
  .panel { background: var(--card); border: 1px solid var(--line); border-radius: 8px;
           padding: 20px; margin-bottom: 20px; }
  form { display: grid; gap: 16px; }
  label, .label { font-weight: 600; display: block; margin-bottom: 4px; }
  input[type=file], select { width: 100%; padding: 8px; border: 1px solid var(--line);
         border-radius: 6px; background: #fff; font: inherit; }
  input[type=range] { width: 100%; accent-color: var(--navy); }
  .row { display: grid; gap: 16px; grid-template-columns: 1fr; }
  @media (min-width: 640px) { .row { grid-template-columns: 1fr 1fr; } }
  button, .button { background: var(--navy); color: #fff; border: 0; border-radius: 6px;
         padding: 12px 20px; font: inherit; font-weight: 700; cursor: pointer;
         text-decoration: none; display: inline-block; }
  button:hover, .button:hover { background: #1b3a66; }
  .button.gold { background: var(--gold); color: var(--ink); }
  .button.gold:hover { background: #ffc61f; }
  :focus-visible { outline: 3px solid var(--gold); outline-offset: 2px; }
  .error { background: #fdecea; border: 1px solid #f1b4ae; color: #7a1a14;
           padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; }
  .images { display: grid; gap: 16px; grid-template-columns: 1fr; }
  @media (min-width: 720px) { .images { grid-template-columns: 1fr 1fr; } }
  .images img { width: 100%; height: auto; border-radius: 6px; border: 1px solid var(--line); }
  .caption { font-weight: 600; margin: 0 0 6px; }
  .risk { display: inline-block; color: #fff; font-weight: 800; padding: 4px 12px;
          border-radius: 4px; }
  .risk.High { background: var(--high); } .risk.Medium { background: var(--medium); }
  .risk.Low { background: var(--low); }  .risk.None { background: var(--none); }
  table { border-collapse: collapse; width: 100%; margin: 12px 0; }
  td { padding: 6px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
  td:first-child { color: var(--muted); width: 40%; }
  .note { color: var(--muted); font-size: .9rem; }
  footer { color: var(--muted); font-size: .85rem; margin-top: 24px; }
</style>
</head>
<body>
<main>
  <h1><span>Privacy</span>Shield</h1>
  <p class="tagline">Upload a photo. PrivacyShield hides faces, shows what the file reveals
     about you, and gives you a clean copy to share. Photos are processed in memory and never saved.</p>

  {% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}

  <div class="panel">
    <form method="POST" action="/process" enctype="multipart/form-data">
      <div>
        <label for="photo">Photo ({{ 'JPG, PNG or HEIC' if heic else 'JPG or PNG' }}, up to {{ max_mb }} MB)</label>
        <input id="photo" type="file" name="photo" accept="image/*" required>
      </div>
      <div class="row">
        <div>
          <label for="mode">How to hide faces</label>
          <select id="mode" name="mode">
            {% for key, name in modes.items() %}
            <option value="{{ key }}" {{ 'selected' if key == mode else '' }}>{{ name }}</option>
            {% endfor %}
          </select>
        </div>
        <div>
          <label for="strength">Strength: <output id="strength_out">{{ strength }}</output></label>
          <input id="strength" type="range" name="strength" min="1" max="10"
                 value="{{ strength }}" oninput="strength_out.value = this.value">
        </div>
      </div>
      <p class="note">Blur is the weakest option because a strong viewer can sometimes still
         recognize a blurred face. Pixelate and Black box hide more.</p>
      <div><button type="submit">Protect photo</button></div>
    </form>
  </div>

  {% if result %}
  <div class="panel">
    <h2 style="margin-top:0">Result</h2>
    <p>{{ result.faces }} face{{ '' if result.faces == 1 else 's' }} hidden.
       Your download has all metadata removed.</p>
    <div class="images">
      <div><p class="caption">Original</p><img src="{{ result.original }}" alt="Original photo"></div>
      <div><p class="caption">Protected</p><img src="{{ result.protected }}" alt="Protected photo"></div>
    </div>
    <p style="margin-top:16px">
      <a class="button gold" download="privacyshield.jpg" href="{{ result.protected }}">Download protected photo</a>
    </p>
    {% if result.faces == 0 %}
    <p class="note">No faces were found. Detection works best on faces that look toward the camera.</p>
    {% endif %}
  </div>

  <div class="panel">
    <h2 style="margin-top:0">What this photo exposed</h2>
    <p><span class="risk {{ meta.risk }}">{{ meta.risk }} exposure</span>
       {% for reason in meta.reasons %} {{ reason }}{% endfor %}</p>
    {% if meta.gps %}
    <table>
      <tr><td>GPS location</td>
          <td>{{ meta.gps.latitude }}, {{ meta.gps.longitude }}
              (<a href="{{ meta.gps.map_url }}" target="_blank" rel="noopener noreferrer">open map</a>)</td></tr>
    </table>
    {% endif %}
    {% if meta.fields %}
    <table>
      {% for label, value in meta.fields %}<tr><td>{{ label }}</td><td>{{ value }}</td></tr>{% endfor %}
    </table>
    {% endif %}
    <p class="note">{{ meta.count }} metadata tag{{ '' if meta.count == 1 else 's' }} found in the original file.
       The protected copy contains none of them.</p>
  </div>
  {% endif %}

  <footer>host={{ host }}</footer>
</main>
</body>
</html>
"""


def render_page(**values):
    """Render the page, filling in defaults for anything the caller leaves out."""
    values.setdefault("error", None)
    values.setdefault("result", None)
    values.setdefault("meta", None)
    values.setdefault("mode", "pixelate")
    values.setdefault("strength", 6)
    return render_template_string(
        PAGE,
        modes=MODES,
        heic=HEIC_SUPPORTED,
        max_mb=MAX_UPLOAD_MB,
        host=hostname,
        **values,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    """Show the upload form. Required route for the final project."""
    return render_page()


@app.route("/process", methods=["POST"])
def process():
    """Handle an upload: read metadata, find faces, hide them, show the results."""
    # Section 1: read the form values and keep them within allowed limits
    mode = request.form.get("mode", "pixelate")
    if mode not in MODES:
        mode = "pixelate"
    strength = min(10, max(1, request.form.get("strength", 6, type=int)))

    file = request.files.get("photo")
    if file is None or file.filename == "":
        return render_page(error="Choose a photo first.", mode=mode, strength=strength)

    # Section 2: open the image (in memory only) and read its metadata
    try:
        img = Image.open(io.BytesIO(file.read()))
        meta = read_metadata(img)
        bgr = prepare_image(img)
    except Exception:
        hint = "" if HEIC_SUPPORTED else " HEIC photos are not supported; export as JPG first."
        return render_page(
            error="That file could not be read as an image." + hint,
            mode=mode,
            strength=strength,
        )

    # Section 3: find and hide faces
    boxes = detect_faces(bgr)
    protected = protect_faces(bgr, boxes, mode, strength)

    # Section 4: build the page
    result = {
        "faces": len(boxes),
        "original": to_data_uri(bgr, 80),
        "protected": to_data_uri(protected, 90),
    }
    return render_page(result=result, meta=meta, mode=mode, strength=strength)


@app.errorhandler(413)
def too_large(_error):
    """Show a friendly message when the upload is bigger than MAX_UPLOAD_MB."""
    return render_page(error=f"That file is too large. The limit is {MAX_UPLOAD_MB} MB."), 413


if __name__ == "__main__":
    # Render tells the app which port to use through the PORT environment variable.
    port = int(os.environ.get("PORT", 80))
    app.run(host="0.0.0.0", port=port)
