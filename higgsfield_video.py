"""
Higgsfield API – video from images (reference-to-video), standalone example.
For the full project use main.py (see README.md).

Run:
    .venv\\Scripts\\python.exe higgsfield_video.py
"""

import urllib.request
from pathlib import Path

from utils import load_api_key

# ===================== SETTINGS =====================

# Model (endpoint ID). Wan 3.0 is the cheapest for testing.
MODEL = "alibaba/wan-3.0/reference-to-video"

# Images of the person (2-4 images = better face match)
IMAGES = [
    "image1.jpg",
    "image2.jpg",
]

# Prompt: describe MOTION and the scene, not the face
PROMPT = (
    "The person from the reference images walks slowly toward the camera "
    "in a sunny park and smiles, slow push-in, natural light, cinematic."
)

DURATION_S = 5         # 2-30 seconds (billed per second!)
RESOLUTION = "480p"    # "480p" for tests, "720p" / "1080p" for final
ASPECT_RATIO = "9:16"  # "16:9", "9:16", "1:1", "4:3", "3:4", "adaptive"
AUDIO = False          # True = also generate audio

OUTPUT = "output.mp4"

# ====================================================


def main():
    load_api_key()
    import higgsfield_client  # import after the key is loaded

    # 1) Upload images to Higgsfield (returns public URLs)
    image_urls = []
    for f in IMAGES:
        if not Path(f).exists():
            raise SystemExit(f"File does not exist: {f}")
        print(f"Uploading {f} ...")
        image_urls.append(higgsfield_client.upload_file(f))

    # 2) Send the request and wait for the result
    last_status = None

    def on_status(status):
        nonlocal last_status
        print(f"Status: {type(status).__name__}")
        last_status = status

    print(f"Sending request to {MODEL} ...")
    result = higgsfield_client.subscribe(
        MODEL,
        arguments={
            "prompt": PROMPT,
            "image_urls": image_urls,
            "duration": DURATION_S,
            "resolution": RESOLUTION,
            "aspect_ratio": ASPECT_RATIO,
            "generate_audio": AUDIO,
        },
        on_enqueue=lambda rid: print(f"Request ID: {rid}"),
        on_queue_update=on_status,
    )

    if isinstance(last_status, (higgsfield_client.Failed, higgsfield_client.NSFW,
                                higgsfield_client.Cancelled)):
        raise SystemExit(f"No video ({type(last_status).__name__}). Response: {result}")

    # 3) Download the video
    video_url = result["video"]["url"]
    print(f"Done: {video_url}")
    urllib.request.urlretrieve(video_url, OUTPUT)
    print(f"Saved as {OUTPUT}")


if __name__ == "__main__":
    main()
