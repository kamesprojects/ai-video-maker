"""
Cut parts of a reference video into new copies. The original is kept.

    python trim_video.py 2-8                       # REFERENCE_VIDEO from config.py
    python trim_video.py 2-8 12-15 --video boxing  # two copies from one video
    python trim_video.py 2.5-8 1:05-1:20           # decimals and minutes:seconds work too
    python trim_video.py 4-11 22-26 --combine      # the parts joined into one video

media/in/reference-video/boxing-video.mp4 -> media/in/reference-video/boxing-video_2-8s.mp4
                                     --combine -> media/in/reference-video/boxing-video_4-11+22-26s.mp4
Times are in seconds; cutting is frame-accurate (the video is re-encoded).
"""

import sys
from pathlib import Path
from typing import NamedTuple

import settings
from utils import (ENCODE_ARGS, QUALITY_ARGS, find_one_video, file_size_mb, has_audio,
                   run_ffmpeg, video_duration)

USAGE = ("Usage: python trim_video.py START-END [START-END ...] [--video NAME] [--combine], "
         "e.g. 2-8 12-15")


class Range(NamedTuple):
    start: float
    end: float
    label: str   # as typed, for the file name: "2-8", "1:05-1:20" -> "1m05-1m20"


def parse_time(text: str) -> float:
    """"8", "2.5" or "1:05" (minutes:seconds) -> seconds."""
    try:
        if ":" in text:
            minutes, seconds = text.split(":")
            return int(minutes) * 60 + float(seconds)
        return float(text)
    except ValueError:
        raise SystemExit(f"Not a time: '{text}'. Use seconds (8, 2.5) or minutes:seconds (1:05).")


def parse_range(text: str) -> Range:
    """"2-8" -> Range(2.0, 8.0, "2-8")."""
    parts = text.split("-")
    if len(parts) != 2 or not all(parts):
        raise SystemExit(f"Not a range: '{text}'. {USAGE}")
    start, end = parse_time(parts[0]), parse_time(parts[1])
    if start >= end:
        raise SystemExit(f"Range '{text}': start must be before end.")
    return Range(start, end, text.replace(":", "m"))


def parse_args(argv: list[str]) -> tuple[list[Range], str | None, bool]:
    """START-END ... [--video NAME] [--combine] -> (ranges, video name or None, combine)."""
    args, video = list(argv), None
    combine = "--combine" in args
    args = [a for a in args if a != "--combine"]
    if "--video" in args:
        i = args.index("--video")
        if i + 1 >= len(args):
            raise SystemExit("--video needs a value, e.g. --video boxing")
        video = args.pop(i + 1)
        args.pop(i)
    if not args:
        raise SystemExit(USAGE)
    return [parse_range(a) for a in args], video, combine


def fit_to_video(cut: Range, seconds: float) -> Range:
    """Shorten a range that runs past the end of the video; exit if it starts after it."""
    if cut.start >= seconds:
        raise SystemExit(f"Range {cut.label}: the video is only {seconds:.1f} s long.")
    if cut.end > seconds:
        print(f"Note:  range {cut.label} ends after the video, cutting to {seconds:.1f} s")
        return Range(cut.start, seconds, f"{cut.start:g}-{seconds:.1f}")   # name = real content
    return cut


def trimmed_path(video: Path, cut: Range) -> Path:
    return video.with_name(f"{video.stem}_{cut.label}s.mp4")


def trim(video: Path, cut: Range) -> Path:
    """Write the part start..end of the video as a new MP4 next to it."""
    output = trimmed_path(video, cut)
    run_ffmpeg([
        "-ss", f"{cut.start:.3f}", "-i", str(video), "-t", f"{cut.end - cut.start:.3f}",
        *QUALITY_ARGS,
        str(output),
    ])
    print(f"Done:  {video.name} {cut.start:g}-{cut.end:g} s -> {output.name} "
          f"({video_duration(output):.1f} s, {file_size_mb(output):.1f} MB)")
    return output


def combined_path(video: Path, cuts: list[Range]) -> Path:
    return video.with_name(f"{video.stem}_{'+'.join(c.label for c in cuts)}s.mp4")


def concat_filter(cuts: list[Range], audio: bool) -> str:
    """ffmpeg filter that cuts every range and joins them in order into [v] (+ [a])."""
    parts, inputs = [], ""
    for i, cut in enumerate(cuts):
        span = f"start={cut.start:.3f}:end={cut.end:.3f}"
        parts.append(f"[0:v]trim={span},setpts=PTS-STARTPTS[v{i}]")
        inputs += f"[v{i}]"
        if audio:
            parts.append(f"[0:a]atrim={span},asetpts=PTS-STARTPTS[a{i}]")
            inputs += f"[a{i}]"
    outputs = "[v][a]" if audio else "[v]"
    parts.append(f"{inputs}concat=n={len(cuts)}:v=1:a={int(audio)}{outputs}")
    return ";".join(parts)


def combine(video: Path, cuts: list[Range]) -> Path:
    """Write all ranges joined in order as one new MP4 next to the video."""
    output = combined_path(video, cuts)
    audio = has_audio(video)
    maps = ["-map", "[v]", "-map", "[a]"] if audio else ["-map", "[v]"]
    run_ffmpeg(["-i", str(video), "-filter_complex", concat_filter(cuts, audio),
                *maps, *ENCODE_ARGS, str(output)])
    print(f"Done:  {video.name} {' + '.join(f'{c.start:g}-{c.end:g}' for c in cuts)} s -> "
          f"{output.name} ({video_duration(output):.1f} s, {file_size_mb(output):.1f} MB)")
    return output


def main():
    ranges, name, join = parse_args(sys.argv[1:])
    video = find_one_video(settings.IN_VIDEO_DIR, name or settings.REFERENCE_VIDEO)
    seconds = video_duration(video)
    cuts = [fit_to_video(cut, seconds) for cut in ranges]
    if join and len(cuts) > 1:
        combine(video, cuts)
        return
    for cut in cuts:
        trim(video, cut)


if __name__ == "__main__":
    main()
