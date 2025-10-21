#!/usr/bin/env python3
"""
YouTube Thumbnail Downloader (Interactive Version)
--------------------------------------------------
Prompts user for a YouTube URL, extracts the video ID,
downloads the thumbnail (best available quality), and saves it to disk.

Features:
- Works with youtube.com, youtu.be, shorts, and embed links
- Attempts multiple quality levels (maxres, sd, hq, mq, default)
- Displays image dimensions and file size
- Handles invalid URLs gracefully
"""

import os
import re
import io
import pathlib
from urllib.parse import urlparse, parse_qs
import requests

# Optional: show dimensions if Pillow installed
try:
    from PIL import Image  # pip install Pillow
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Output folder
OUT_DIR = pathlib.Path("thumbnails")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Thumbnail quality order
THUMB_QUALITIES = [
    "maxresdefault.jpg",
    "sddefault.jpg",
    "hqdefault.jpg",
    "mqdefault.jpg",
    "default.jpg",
]


def extract_video_id(url: str):
    """Extracts YouTube video ID from various formats."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path

    # watch?v=VIDEOID
    if "youtube.com" in host:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]

        # /shorts/VIDEOID
        m = re.match(r"^/shorts/([A-Za-z0-9_-]{6,})", path)
        if m:
            return m.group(1)

        # /embed/VIDEOID
        m = re.match(r"^/embed/([A-Za-z0-9_-]{6,})", path)
        if m:
            return m.group(1)

    # youtu.be/VIDEOID
    if "youtu.be" in host:
        m = re.match(r"^/([A-Za-z0-9_-]{6,})", path)
        if m:
            return m.group(1)

    # fallback
    m = re.search(r"([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


def download_image(url):
    """Downloads image bytes, returns None if unavailable."""
    try:
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image/"):
            return r.content
    except requests.RequestException:
        pass
    return None


def get_image_info(img_bytes):
    """Returns (width, height, size_kb)."""
    size_kb = len(img_bytes) / 1024
    dims = None
    if PIL_AVAILABLE:
        try:
            with Image.open(io.BytesIO(img_bytes)) as im:
                dims = (im.width, im.height)
        except Exception:
            pass
    return dims, size_kb


def download_thumbnail(video_url: str):
    print("\n🎬 YouTube Thumbnail Downloader")
    print("===============================")
    video_id = extract_video_id(video_url)
    if not video_id:
        print("❌ Could not extract a valid YouTube video ID.")
        return

    print(f"Video ID: {video_id}")
    print("Attempting to download thumbnail in highest quality available...")

    img_bytes = None
    quality = None
    for q in THUMB_QUALITIES:
        thumb_url = f"https://img.youtube.com/vi/{video_id}/{q}"
        img_bytes = download_image(thumb_url)
        if img_bytes:
            quality = q
            break

    if not img_bytes:
        print("❌ Thumbnail not found.")
        return

    filename = OUT_DIR / f"{video_id}_{quality.replace('.jpg','')}.jpg"
    with open(filename, "wb") as f:
        f.write(img_bytes)

    dims, size_kb = get_image_info(img_bytes)
    print(f"✅ Thumbnail saved as: {filename}")
    print(f"File size: {size_kb:.1f} KB")
    if dims:
        print(f"Dimensions: {dims[0]} x {dims[1]}")
    print("Download complete!\n")


if __name__ == "__main__":
    url = input("Enter a YouTube video URL: ").strip()
    if url:
        download_thumbnail(url)
    else:
        print("No URL entered. Exiting.")