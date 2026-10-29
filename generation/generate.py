"""Generation via the Higgsfield API: upload, request, wait, download."""

import urllib.request
from pathlib import Path

from models import Model
from settings import TIMEOUT_S   # SDK default is 90 s, too short to upload a video on a slow connection
from utils import load_api_key


def generate(model: Model, prompt: str, video: Path, images: list[Path],
             settings: dict, output: Path, record: dict) -> Path:
    """Run a PAID generation, save the video to `output` and return it.

    `record` is filled with request_id, status, URLs and errors as they happen.
    """
    load_api_key()
    import higgsfield_client  # import after the key is loaded
    client = higgsfield_client.SyncClient(timeout=TIMEOUT_S)

    # 1) Upload files
    print("\nUploading files ...")
    video_url = client.upload_file(video)
    image_urls = [client.upload_file(f) for f in images]
    record["uploaded"] = {"video_url": video_url, "image_urls": image_urls}

    # 2) Send the request and wait for the result
    last_status = None

    def on_status(status):
        nonlocal last_status
        if type(status) is not type(last_status):
            print(f"Status: {type(status).__name__}")
        last_status = status
        record["status"] = type(status).__name__.lower()

    def on_enqueue(request_id):
        print(f"Request ID: {request_id}")
        record["request_id"] = request_id

    print(f"Sending request to {model.endpoint} ...")
    result = client.subscribe(
        model.endpoint,
        arguments=model.arguments(prompt, video_url, image_urls, settings),
        on_enqueue=on_enqueue,
        on_queue_update=on_status,
    )

    # The SDK does not raise on failure, so check the final status
    record["response"] = result
    reason = f" Reason: {result['error']}" if isinstance(result, dict) and result.get("error") else ""
    if isinstance(last_status, higgsfield_client.NSFW):
        raise SystemExit(f"Rejected by moderation (NSFW), not charged.{reason}")
    if isinstance(last_status, higgsfield_client.Cancelled):
        raise SystemExit(f"Request was cancelled, not charged.{reason}")
    if isinstance(last_status, higgsfield_client.Failed):
        raise SystemExit(f"Generation failed, not charged.{reason or f' Response: {result}'}")

    result_url = (result.get("video") or {}).get("url")
    if not result_url:
        raise SystemExit(f"No video URL in the response. Response: {result}")
    print(f"Done: {result_url}")

    # 3) Download
    output.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(result_url, output)
    print(f"Saved as {output}")
    return output
