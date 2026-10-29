"""
Higgsfield API – reference video + images -> video (Wan 3.0 / Seedance 2.5 / Kling O3)

Settings: config.example.py (defaults) and your config.py. Prompts: prompt.py. See README.md.

    .venv\\Scripts\\python.exe main.py --help              # all arguments and examples
    .venv\\Scripts\\python.exe main.py --test              # check only, nothing is billed
    .venv\\Scripts\\python.exe main.py                     # wan, 480p, one-person
    .venv\\Scripts\\python.exe main.py seedance 720p four-people
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import settings
from choices import Key, ModelName, PromptName, Resolution
from generation import generate
from generation.record import (NOT_CHARGED, cost_dict, estimate, new_record, now,
                               planned_estimate, save_record, video_info)
from models import GenjutsuLight, Kling, Seedance, Wan
from prompt import get_prompt
from utils import (IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, describe_size, file_size_mb,
                   has_audio, list_files, needs_compression, prepare_video,
                   select_file, video_duration, video_size)

# Settings: config.example.py + your config.py (see settings.py).
MAX_DURATION = settings.MAX_DURATION
MAX_UPLOAD_MB = settings.MAX_UPLOAD_MB
DEFAULT_MODEL = settings.DEFAULT_MODEL
DEFAULT_RESOLUTION = settings.DEFAULT_RESOLUTION
DEFAULT_PROMPT = settings.DEFAULT_PROMPT
IN_VIDEO = settings.IN_VIDEO_DIR
IN_IMAGES = settings.IN_IMAGES_DIR
OUT = settings.OUT_DIR
TMP = settings.TMP_DIR

MODELS = {m.name: m for m in [
    Wan(audio=settings.GENERATE_AUDIO, max_duration=MAX_DURATION),
    Seedance(audio=settings.GENERATE_AUDIO, max_duration=MAX_DURATION),
    Kling(),
    GenjutsuLight(),
]}


FLAGS = ["--test", "--mute"]
VALUE_OPTIONS = ["--video", "--images"]   # take a value: --video x or --video=x


class Args(NamedTuple):
    model: str
    resolution: str
    prompt: str
    test: bool
    mute: bool
    video: str | None = None          # None = the only video in the folder
    images: list[str] | None = None   # None = all images, sorted by name


def options(names, default) -> str:
    return ", ".join(f"{n} (default)" if n == default else n for n in names)


def help_text() -> str:
    return f"""Usage: python main.py [model] [resolution] [prompt] [--video NAME] [--images A,B]
                      [--test] [--mute]

Arguments can be in any order. Anything you leave out uses the default from config.py
(or config.example.py).

  model           {options(MODELS, DEFAULT_MODEL)}
  resolution      {options(Resolution, DEFAULT_RESOLUTION)}
  prompt          {options(PromptName, DEFAULT_PROMPT)}
                  (edit in prompt.py; tmp-prompt = text in {settings.TMP_PROMPT_FILE.as_posix()})

  --video NAME    which video from {IN_VIDEO.as_posix()}/ to use
                  (default: the only one there; extension optional)
  --images A,B    which images from {IN_IMAGES.as_posix()}/ to use, in this order:
                  A = Image 1, B = Image 2... (default: all, sorted by name)
  --test          free check: print what would be sent, upload and bill nothing
  --mute          upload the reference video without sound
                  (the original in media/in is not changed)
  -h, --help      show this help

Output:   {OUT.as_posix()}/<model>_<resolution>_<prompt>_<date>.mp4

Examples:
  python main.py --test                       check the defaults (free)
  python main.py                              generate: {DEFAULT_MODEL}, {DEFAULT_RESOLUTION}, {DEFAULT_PROMPT}
  python main.py seedance 720p --test         check another model and resolution
  python main.py kling 1080p four-people      generate with Kling and the 4-people prompt
  python main.py --mute                       generate, reference video sent without sound
  python main.py --video song --images kristian,kamil --test
                                              check a chosen video and 2 images in that order

Without --test every run is a PAID generation. See README.md for details."""


def split_value_options(argv: list[str]) -> tuple[list[str], dict[str, str]]:
    """Pull out --video / --images and their values; return (other args, values)."""
    rest, values = [], {}
    tokens = iter(argv)
    for token in tokens:
        key, has_equals, value = token.partition("=")
        if key.lower() not in VALUE_OPTIONS:
            rest.append(token)
            continue
        value = value if has_equals else next(tokens, "")
        if not value or value.startswith("--"):
            raise SystemExit(f"{key} needs a value, e.g. {key} NAME")
        values[key.lower()] = value
    return rest, values


def parse_args(argv: list[str]) -> Args:
    """Arguments in any order -> Args."""
    rest, values = split_value_options(argv)
    args = [a.lower() for a in rest]
    if "-h" in args or "--help" in args:
        print(help_text())
        raise SystemExit(0)
    test = "--test" in args
    mute = "--mute" in args or settings.MUTE_REFERENCE_VIDEO
    args = [a for a in args if a not in FLAGS]

    unknown = [a for a in args if a not in MODELS and a not in list(Resolution) and a not in list(PromptName)]
    if unknown:
        raise SystemExit(
            f"Unknown argument: {', '.join(unknown)}. Models: {', '.join(MODELS)} | "
            f"resolutions: {', '.join(Resolution)} | prompts: {', '.join(PromptName)}\n"
            f"Run python main.py --help for usage."
        )

    def pick(options, default):
        return next((a for a in args if a in options), default)

    return Args(parse_key(ModelName, pick(MODELS, DEFAULT_MODEL), "DEFAULT_MODEL"),
                parse_key(Resolution, pick(list(Resolution), DEFAULT_RESOLUTION),
                          "DEFAULT_RESOLUTION"),
                parse_key(PromptName, pick(list(PromptName), DEFAULT_PROMPT), "DEFAULT_PROMPT"),
                test, mute,
                values.get("--video") or settings.REFERENCE_VIDEO,
                name_list(values.get("--images") or settings.REFERENCE_IMAGES))


def name_list(names: str | list[str] | None) -> list[str] | None:
    """"a, b" or ["a", "b"] -> ["a", "b"]; empty -> None (= all images)."""
    if isinstance(names, str):
        names = names.split(",")
    cleaned = [n.strip() for n in names or [] if n.strip()]
    return cleaned or None


def parse_key(keys: type[Key], value, setting: str) -> Key:
    """"wan" or ModelName.WAN -> ModelName.WAN; exit with the options if unknown."""
    try:
        return keys(value)
    except ValueError:
        raise SystemExit(f"Unknown {keys.__name__} '{value}' (check {setting} in config.py). "
                         f"Options: {', '.join(keys)}")


def check_images(model, images: list[Path]):
    if model.max_images and len(images) > model.max_images:
        raise SystemExit(f"{model.name} accepts at most {model.max_images} images "
                         f"(got {len(images)}). Choose them with --images.")


def find_video(name: str | None) -> Path:
    """The video called `name`, or the only video in the folder."""
    videos = list_files(IN_VIDEO, VIDEO_EXTENSIONS)
    if name:
        return select_file(videos, name, IN_VIDEO)
    if len(videos) == 1:
        return videos[0]
    if not videos:
        raise SystemExit(f"No video in {IN_VIDEO.as_posix()}/.")
    raise SystemExit(f"{IN_VIDEO.as_posix()}/ has {len(videos)} videos: "
                     f"{', '.join(v.name for v in videos)}. Choose one with --video NAME.")


def find_images(names: list[str] | None) -> list[Path]:
    """The images in the given order, or all images sorted by name."""
    images = list_files(IN_IMAGES, IMAGE_EXTENSIONS)
    if names:
        return [select_file(images, n, IN_IMAGES) for n in names]
    if not images:
        raise SystemExit(f"No images in {IN_IMAGES.as_posix()}/.")
    return images


def audio_summary(video: Path, mute: bool) -> str:
    if not has_audio(video):
        return "none in the video"
    return "removed before upload (--mute)" if mute else "sent with the video"


def preview(text: str, length: int = 70) -> str:
    one_line = " ".join(text.split())
    return one_line if len(one_line) <= length else one_line[:length] + "..."


def print_summary(args: Args, model, prompt_text, video, images, model_settings, cost):
    print(f"Config:     {settings.SOURCE}")
    print(f"Model:      {args.model} ({model.endpoint})")
    print(f"Prompt:     {args.prompt}: {preview(prompt_text)}")
    print(f"Video:      {video.name} ({video_duration(video):.1f} s, {file_size_mb(video):.1f} MB, "
          f"{describe_size(video_size(video))})")
    print(f"Audio:      {audio_summary(video, args.mute)}")
    seconds = model.upload_seconds(MAX_DURATION)
    if args.mute or needs_compression(video, seconds, MAX_UPLOAD_MB):
        print(f"Upload:     prepared copy in {TMP.as_posix()}/, max {seconds} s, H.264")
    print(f"Parameters: {model_settings}")
    for i, f in enumerate(images, 1):
        print(f"Image {i}:    {f.name}")
    print(f"Est. cost:  {cost}")


def output_stem(args: Args) -> Path:
    """media/out/<model>_<resolution>_<prompt>[_muted]_<date>; the .mp4 and .json share it."""
    muted = "_muted" if args.mute else ""
    return OUT / f"{args.model}_{args.resolution}_{args.prompt}{muted}_{datetime.now():%Y%m%d_%H%M%S}"


def run(args: Args, model, prompt_text, video, images, model_settings, planned):
    """The PAID part: prepare, generate, and save a JSON record (also on failure)."""
    stem = output_stem(args)
    record = new_record(args, model, prompt_text, video, images, model_settings, planned)
    try:
        upload = prepare_video(video, model.upload_seconds(MAX_DURATION), MAX_UPLOAD_MB, TMP,
                               audio=not args.mute)
        record["input"]["uploaded_video"] = video_info(upload)
        output = generate(model, prompt_text, upload, images, model_settings,
                          stem.with_suffix(".mp4"), record)
    except (SystemExit, Exception) as error:
        if record["status"] in ("started", "queued", "inprogress"):
            record["status"] = "error"
        record.update(error=str(error), finished_at=now(), cost=cost_dict(NOT_CHARGED))
        save_record(stem.with_suffix(".json"), record)
        raise

    record["output"] = video_info(output)
    cost = estimate(args.model, str(args.resolution), model_settings, video,
                    record["output"]["seconds"], record["input"]["uploaded_video"]["seconds"])
    record.update(status="completed", finished_at=now(), cost=cost_dict(cost))
    print(f"Output:     {record['output']['seconds']} s, {record['output']['resolution']}")
    print(f"Est. cost:  {cost}")
    save_record(stem.with_suffix(".json"), record)


def main():
    args = parse_args(sys.argv[1:])
    model = MODELS[args.model]
    prompt_text = get_prompt(args.prompt)
    video, images = find_video(args.video), find_images(args.images)
    check_images(model, images)
    model_settings = model.settings(video, str(args.resolution))
    planned = planned_estimate(model, str(args.resolution), model_settings, video)

    print_summary(args, model, prompt_text, video, images, model_settings, planned)
    if args.test:
        print("\n--test: nothing was uploaded or generated.")
        return
    run(args, model, prompt_text, video, images, model_settings, planned)


if __name__ == "__main__":
    main()
