"""Generation via the Higgsfield API: upload, request, wait, download."""

import urllib.request
from datetime import datetime
from pathlib import Path

from models import Model
from settings import TIMEOUT_S   # SDK default is 90 s, too short to upload a video on a slow connection
from utils import load_api_key


def generate(model: Model, prompt: str, video: Path, images: list[Path],
             settings: dict, out_dir: Path, file_prefix: str) -> Path:
    """Run a PAID generation and return the path of the saved video."""
    load_api_key()
    import higgsfield_client  # import after the key is loaded
    client = higgsfield_client.SyncClient(timeout=TIMEOUT_S)

    # 1) Upload files
    print("\nUploading files ...")
    video_url = client.upload_file(video)
    image_urls = [client.upload_file(f) for f in images]

    # 2) Send the request and wait for the result
    last_status = None

    def on_status(status):
        nonlocal last_status
        if type(status) is not type(last_status):
            print(f"Status: {type(status).__name__}")
        last_status = status

    print(f"Sending request to {model.endpoint} ...")
    result = client.subscribe(
        model.endpoint,
        arguments=model.arguments(prompt, video_url, image_urls, settings),
        on_enqueue=lambda rid: print(f"Request ID: {rid}"),
        on_queue_update=on_status,
    )

    # The SDK does not raise on failure, so check the final status
    if isinstance(last_status, higgsfield_client.NSFW):
        raise SystemExit("Rejected by moderation (NSFW). No video.")
    if isinstance(last_status, higgsfield_client.Cancelled):
        raise SystemExit("Request was cancelled. No video.")
    if isinstance(last_status, higgsfield_client.Failed):
        raise SystemExit(f"Generation failed. Response: {result}")

    result_url = (result.get("video") or {}).get("url")
    if not result_url:
        raise SystemExit(f"No video URL in the response. Response: {result}")
    print(f"Done: {result_url}")

    # 3) Download
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{file_prefix}_{datetime.now():%Y%m%d_%H%M%S}.mp4"
    urllib.request.urlretrieve(result_url, output)
    print(f"Saved as {output}")
    return output
