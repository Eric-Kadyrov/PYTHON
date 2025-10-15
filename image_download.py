import os
import urllib.request
from datetime import datetime

# === Settings ===
# List of image URLs (you can add more for the bonus part)
image_urls = [
    "https://picsum.photos/800/600",
    "https://picsum.photos/600/400",
    "https://picsum.photos/1200/800"
]

# Create a downloads folder if it doesn't exist
os.makedirs("downloads", exist_ok=True)

# Download each image
for i, url in enumerate(image_urls, start=1):
    # Create a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"downloads/image_{i}_{timestamp}.jpg"

    print(f"Downloading image {i} from {url}...")

    # Download and save the image
    urllib.request.urlretrieve(url, filename)

    # Get file size in KB
    file_size_kb = os.path.getsize(filename) / 1024
    print(f"✅ Saved as {filename} ({file_size_kb:.2f} KB)\n")

print("All downloads completed successfully!")