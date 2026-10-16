"""
Higgsfield API – reference video + images -> video (Wan 3.0 / Seedance 2.5 / Kling O3)

Prompts are in prompt.py, inputs in media/in/, results in media/out/. See README.md.

    .venv\\Scripts\\python.exe main.py --help              # all arguments and examples
    .venv\\Scripts\\python.exe main.py --test              # check only, nothing is billed
    .venv\\Scripts\\python.exe main.py                     # wan, 480p, one-person
    .venv\\Scripts\\python.exe main.py seedance 720p four-people
"""

import sys
from pathlib import Path
from typing import NamedTuple

from generation import generate
from models import Kling, Seedance, Wan
from prompt import DEFAULT_PROMPT, PROMPTS
from utils import (IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, describe_size, file_size_mb,
                   has_audio, list_files, needs_compression, prepare_video,
                   video_duration, video_size)

# ===================== SETTINGS =====================

MAX_DURATION = 20      # longer reference videos are trimmed to this before upload
MAX_UPLOAD_MB = 10     # bigger reference videos are compressed before upload
AUDIO = False          # wan/seedance; kling has no audio

MODELS = {
    "wan": Wan(audio=AUDIO, max_duration=MAX_DURATION),
    "seedance": Seedance(audio=AUDIO, max_duration=MAX_DURATION),
    "kling": Kling(),
}
DEFAULT_MODEL = "wan"

RESOLUTIONS = ["480p", "720p", "1080p"]
DEFAULT_RESOLUTION = "480p"

IN_VIDEO = Path("media/in/reference-video")
IN_IMAGES = Path("media/in/reference-images")
OUT = Path("media/out")
TMP = Path("media/tmp")   # compressed copies of reference videos

# ====================================================


FLAGS = ["--test", "--mute"]


class Args(NamedTuple):
    model: str
    resolution: str
    prompt: str
    test: bool
    mute: bool


def options(names, default) -> str:
    return ", ".join(f"{n} (default)" if n == default else n for n in names)


def help_text() -> str:
    return f"""Usage: python main.py [model] [resolution] [prompt] [--test] [--mute]

Arguments can be in any order. Anything you leave out uses the default.

  model        {options(MODELS, DEFAULT_MODEL)}
  resolution   {options(RESOLUTIONS, DEFAULT_RESOLUTION)}
  prompt       {options(PROMPTS, DEFAULT_PROMPT)}   (edit in prompt.py)

  --test       free check: print what would be sent, upload and bill nothing
  --mute       upload the reference video without sound
               (the original in media/in is not changed)
  -h, --help   show this help

Inputs:   1 video in {IN_VIDEO.as_posix()}/, images in {IN_IMAGES.as_posix()}/
Output:   {OUT.as_posix()}/<model>_<resolution>_<prompt>_<date>.mp4

Examples:
  python main.py --test                       check the defaults (free)
  python main.py                              generate: {DEFAULT_MODEL}, {DEFAULT_RESOLUTION}, {DEFAULT_PROMPT}
  python main.py seedance 720p --test         check another model and resolution
  python main.py kling 1080p four-people      generate with Kling and the 4-people prompt
  python main.py --mute                       generate, reference video sent without sound

Without --test every run is a PAID generation. See README.md for details."""


def parse_args(argv: list[str]) -> Args:
    """Arguments in any order -> Args(model, resolution, prompt, test, mute)."""
    args = [a.lower() for a in argv]
    if "-h" in args or "--help" in args:
        print(help_text())
        raise SystemExit(0)
    test, mute = "--test" in args, "--mute" in args
    args = [a for a in args if a not in FLAGS]

    unknown = [a for a in args if a not in MODELS and a not in RESOLUTIONS and a not in PROMPTS]
    if unknown:
        raise SystemExit(
            f"Unknown argument: {', '.join(unknown)}. Models: {', '.join(MODELS)} | "
            f"resolutions: {', '.join(RESOLUTIONS)} | prompts: {', '.join(PROMPTS)}\n"
            f"Run python main.py --help for usage."
        )

    def pick(options, default):
        return next((a for a in args if a in options), default)

    return Args(pick(MODELS, DEFAULT_MODEL), pick(RESOLUTIONS, DEFAULT_RESOLUTION),
                pick(PROMPTS, DEFAULT_PROMPT), test, mute)


def find_inputs() -> tuple[Path, list[Path]]:
    """The one reference video and the reference images."""
    videos = list_files(IN_VIDEO, VIDEO_EXTENSIONS)
    images = list_files(IN_IMAGES, IMAGE_EXTENSIONS)
    if len(videos) != 1:
        raise SystemExit(f"{IN_VIDEO} must contain exactly 1 video (found: {len(videos)}).")
    if not images:
        raise SystemExit(f"{IN_IMAGES} contains no images.")
    return videos[0], images


def audio_summary(video: Path, mute: bool) -> str:
    if not has_audio(video):
        return "none in the video"
    return "removed before upload (--mute)" if mute else "sent with the video"


def print_summary(args: Args, model, video, images, settings):
    print(f"Model:      {args.model} ({model.endpoint})")
    print(f"Prompt:     {args.prompt}")
    print(f"Video:      {video.name} ({video_duration(video):.1f} s, {file_size_mb(video):.1f} MB, "
          f"{describe_size(video_size(video))})")
    print(f"Audio:      {audio_summary(video, args.mute)}")
    if args.mute or needs_compression(video, MAX_DURATION, MAX_UPLOAD_MB):
        print(f"Upload:     prepared copy in {TMP.as_posix()}/, max {MAX_DURATION} s, H.264")
    print(f"Parameters: {settings}")
    for i, f in enumerate(images, 1):
        print(f"Image {i}:    {f.name}")


def main():
    args = parse_args(sys.argv[1:])
    model = MODELS[args.model]
    video, images = find_inputs()
    settings = model.settings(video, args.resolution)

    print_summary(args, model, video, images, settings)
    if args.test:
        print("\n--test: nothing was uploaded or generated.")
        return

    video = prepare_video(video, MAX_DURATION, MAX_UPLOAD_MB, TMP, audio=not args.mute)
    generate(model, PROMPTS[args.prompt], video, images, settings, OUT,
             f"{args.model}_{args.resolution}_{args.prompt}{'_muted' if args.mute else ''}")


if __name__ == "__main__":
    main()
