"""Shared helpers: files, video metadata, API key."""

import math
import os
import struct
from pathlib import Path

from dotenv import load_dotenv
from mutagen.mp4 import MP4

VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def list_files(folder: Path, extensions: set) -> list[Path]:
    """Files with the given extensions in a folder, sorted by name."""
    folder.mkdir(parents=True, exist_ok=True)
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in extensions)


def video_duration(video: Path) -> float:
    """Video length in seconds."""
    return MP4(video).info.length


def video_size(video: Path):
    """Video width and height (accounting for phone rotation), or None."""
    data = video.read_bytes()

    def boxes(start, end):
        i = start
        while i + 8 <= end:
            size, box_type = struct.unpack(">I4s", data[i:i + 8])
            header = 8
            if size == 1:
                size = struct.unpack(">Q", data[i + 8:i + 16])[0]
                header = 16
            elif size == 0:
                size = end - i
            if size < header:
                return
            yield box_type, i + header, i + size
            i += size

    for box_type, s, e in boxes(0, len(data)):
        if box_type != b"moov":
            continue
        for box_type2, s2, e2 in boxes(s, e):
            if box_type2 != b"trak":
                continue
            for box_type3, s3, _ in boxes(s2, e2):
                if box_type3 != b"tkhd":
                    continue
                version = data[s3]
                matrix = s3 + 4 + (32 if version == 1 else 20) + 16
                _, b = struct.unpack(">ii", data[matrix:matrix + 8])
                w, h = struct.unpack(">II", data[matrix + 36:matrix + 44])
                w, h = w >> 16, h >> 16
                if w and h:  # audio tracks are 0x0
                    return (h, w) if b != 0 else (w, h)
    return None


def closest_aspect_ratio(size, ratios: list[str]) -> str:
    """Pick the allowed ratio ("16:9", ...) closest to the video size."""
    w, h = size

    def distance(ratio):
        rw, rh = ratio.split(":")
        return abs(math.log(w / h) - math.log(int(rw) / int(rh)))

    return min(ratios, key=distance)


def load_api_key():
    """Load HF_KEY from .env.local / .env (API_KEY also works). Never prints the value."""
    load_dotenv(".env.local")
    load_dotenv(".env")
    if not os.getenv("HF_KEY") and os.getenv("API_KEY"):
        os.environ["HF_KEY"] = os.environ["API_KEY"]
    key = os.getenv("HF_KEY")
    if not key:
        raise SystemExit("Error: HF_KEY (or API_KEY) is missing in .env.")
    if ":" not in key:
        raise SystemExit("Error: the key must be in key-id:key-secret format.")
