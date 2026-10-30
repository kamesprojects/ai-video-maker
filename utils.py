"""Shared helpers: files, video metadata, API key."""

import math
import os
import struct
import subprocess
from pathlib import Path

import imageio_ffmpeg
from dotenv import load_dotenv

from settings import MAX_SIDE_PX
from mutagen.mp4 import MP4

VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def list_files(folder: Path, extensions: set) -> list[Path]:
    """Files with the given extensions in a folder, sorted by name."""
    folder.mkdir(parents=True, exist_ok=True)
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in extensions)


def select_file(files: list[Path], name: str, folder: Path) -> Path:
    """The file matching `name`, any case: full name, name without extension,
    or a part of the name that fits exactly one file."""
    wanted = name.lower()
    exact = [f for f in files if wanted in (f.name.lower(), f.stem.lower())]
    partial = [f for f in files if wanted in f.name.lower()]
    for matches in (exact, partial):
        if len(matches) == 1:
            return matches[0]
    available = ", ".join(f.name for f in files) or "nothing"
    problem = "matches several files" if partial else "not found"
    raise SystemExit(f"'{name}' {problem} in {folder.as_posix()}/. Available: {available}")


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


# Scale so the longer side is at most MAX_SIDE_PX (never upscale), keep ratio
SCALE_FILTER = (
    f"scale='if(gte(iw,ih),min({MAX_SIDE_PX},iw),-2)'"
    f":'if(gte(iw,ih),-2,min({MAX_SIDE_PX},ih))'"
)


def file_size_mb(path: Path) -> float:
    return path.stat().st_size / 1_000_000


def needs_compression(video: Path, max_seconds: int, max_mb: float) -> bool:
    """True if the video is too long or too big to upload as is."""
    return video_duration(video) > max_seconds or file_size_mb(video) > max_mb


def has_audio(video: Path) -> bool:
    """True if the video has an audio track."""
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", str(video)]
    info = subprocess.run(command, capture_output=True, text=True).stderr
    return "Audio:" in info


def compress_video(video: Path, max_seconds: int, out_dir: Path, audio: bool = True) -> Path:
    """Re-encode the first `max_seconds` to a small H.264 MP4 in out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{video.stem}_upload{'' if audio else '_muted'}.mp4"
    audio_args = ["-map", "0:a?", "-c:a", "aac", "-b:a", "128k"] if audio else ["-an"]
    run_ffmpeg([
        "-i", str(video), "-t", str(max_seconds),
        "-map", "0:v:0",                    # first video track
        *audio_args,                        # + audio if present, or no audio
        "-vf", SCALE_FILTER,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output),
    ])
    return output


# Good-quality H.264 + AAC MP4 encoding
ENCODE_ARGS = [
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart",
]
# ... of the first video track and the audio (if any)
QUALITY_ARGS = ["-map", "0:v:0", "-map", "0:a?", *ENCODE_ARGS]


def find_one_video(folder: Path, name: str | None) -> Path:
    """The video called `name`, or the only video in the folder."""
    videos = list_files(folder, VIDEO_EXTENSIONS)
    if name:
        return select_file(videos, name, folder)
    if len(videos) == 1:
        return videos[0]
    if not videos:
        raise SystemExit(f"No video in {folder.as_posix()}/.")
    raise SystemExit(f"{folder.as_posix()}/ has {len(videos)} videos: "
                     f"{', '.join(v.name for v in videos)}. Choose one with --video NAME.")


def run_ffmpeg(args: list[str]):
    """Run the bundled ffmpeg; exit with its error message on failure."""
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", *args]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg failed: {result.stderr.strip()}")


def prepare_video(video: Path, max_seconds: int, max_mb: float, out_dir: Path,
                  audio: bool = True) -> Path:
    """Return the video as is, or a trimmed / compressed / muted copy if it needs it.

    The original file is never changed.
    """
    if audio and not needs_compression(video, max_seconds, max_mb):
        return video
    print(f"Preparing {video.name} for upload{'' if audio else ' (without audio)'} ...")
    output = compress_video(video, max_seconds, out_dir, audio)
    print(f"Compressed: {file_size_mb(video):.1f} MB -> {file_size_mb(output):.1f} MB")
    return output


COMMON_ASPECT_RATIOS = ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9"]


def describe_size(size) -> str:
    """Human-readable size, orientation and ratio, e.g. "1080x1920, vertical, ~9:16"."""
    if not size:
        return "unknown size"
    w, h = size
    orientation = "horizontal" if w > h else "vertical" if h > w else "square"
    return f"{w}x{h}, {orientation}, ~{closest_aspect_ratio(size, COMMON_ASPECT_RATIOS)}"


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
