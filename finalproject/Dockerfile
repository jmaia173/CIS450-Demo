# PrivacyShield - Dockerfile
# Build: docker build -t app .      Run: docker run -p 80:80 app
FROM python:3.11-slim

WORKDIR /app

# System libraries OpenCV may need (kept from the course template)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages first so Docker can cache this layer.
# OpenCV is pinned below version 5 in requirements.txt because OpenCV 5
# removed the Haar face detector this app uses.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app (proto/, template/ and media/ are excluded by .dockerignore)
COPY . .

# Render supplies PORT at runtime; app.py reads it and falls back to 80.
EXPOSE 80
CMD ["python", "app.py"]
