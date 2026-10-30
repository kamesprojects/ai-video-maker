"""
Downscale reference videos to a resolution. Saves copies, originals are kept; never upscales.

    python resize_videos.py                       # RESIZE_TO from config.py, all videos
    python resize_videos.py 480p                  # resolution from the command line
    python resize_videos.py 720p --video boxing   # only one video

media/in/reference-video/boxing-video.mp4 -> media/in/reference-video/boxing-video_480p.mp4
"""

import sys
from pathlib import Path

import settings
from choices import Resolution
from utils import (QUALITY_ARGS, VIDEO_EXTENSIONS, describe_size, file_size_mb, list_files,
                   run_ffmpeg, select_file, video_size)


def target_size(size: tuple[int, int], resolution: Resolution) -> tuple[int, int] | None:
    """New width x height with the shorter side = resolution; None if not smaller."""
    w, h = size
    short = int(str(resolution).rstrip("p"))
    if min(w, h) <= short:
        return None
    scale = short / min(w, h)
    return round(w * scale / 2) * 2, round(h * scale / 2) * 2   # even numbers for H.264


def resized_path(video: Path, resolution: Resolution) -> Path:
    return video.with_name(f"{video.stem}_{resolution}.mp4")


def is_resized_copy(video: Path) -> bool:
    """Copies made by this script end with _480p / _720p / _1080p."""
    return any(video.stem.endswith(f"_{r}") for r in Resolution)


def resize(video: Path, resolution: Resolution) -> Path | None:
    """Write a downscaled copy; None if the video is already this small or smaller."""
    size = video_size(video)
    new_size = target_size(size, resolution) if size else None
    if not new_size:
        print(f"Skip:  {video.name} ({describe_size(size)}) is already {resolution} or smaller")
        return None
    output = resized_path(video, resolution)
    run_ffmpeg([
        "-i", str(video),
        "-vf", f"scale={new_size[0]}:{new_size[1]},setsar=1",   # square pixels, exact size
        *QUALITY_ARGS,
        str(output),
    ])
    print(f"Done:  {video.name} {size[0]}x{size[1]}, {file_size_mb(video):.1f} MB -> "
          f"{output.name} {new_size[0]}x{new_size[1]}, {file_size_mb(output):.1f} MB")
    return output


def parse_args(argv: list[str]) -> tuple[Resolution, str | None]:
    """[resolution] [--video NAME] -> (resolution, video name or None for all)."""
    args, video = list(argv), None
    if "--video" in args:
        i = args.index("--video")
        if i + 1 >= len(args):
            raise SystemExit("--video needs a value, e.g. --video boxing")
        video = args.pop(i + 1)
        args.pop(i)
    if len(args) > 1:
        raise SystemExit(f"Too many arguments: {' '.join(args)}. "
                         f"Usage: python resize_videos.py [480p|720p|1080p] [--video NAME]")
    value = args[0].lower() if args else settings.RESIZE_TO
    try:
        return Resolution(value), video
    except ValueError:
        raise SystemExit(f"Unknown resolution '{value}'. Options: {', '.join(Resolution)}")


def videos_to_resize(name: str | None) -> list[Path]:
    """The chosen video, or all originals in the folder (not earlier copies)."""
    videos = list_files(settings.IN_VIDEO_DIR, VIDEO_EXTENSIONS)
    if name:
        return [select_file(videos, name, settings.IN_VIDEO_DIR)]
    originals = [v for v in videos if not is_resized_copy(v)]
    if not originals:
        raise SystemExit(f"No videos in {settings.IN_VIDEO_DIR.as_posix()}/.")
    return originals


def main():
    resolution, name = parse_args(sys.argv[1:])
    for video in videos_to_resize(name):
        resize(video, resolution)


if __name__ == "__main__":
    main()
