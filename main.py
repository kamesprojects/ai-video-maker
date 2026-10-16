"""
Higgsfield API – reference video + images -> video (Wan 3.0 / Seedance 2.5 / Kling O3)

The prompt is in prompt.py, inputs in media/in/, results in media/out/. See README.md.

    .venv\\Scripts\\python.exe main.py --test              # check only, nothing is billed
    .venv\\Scripts\\python.exe main.py                     # wan, 480p
    .venv\\Scripts\\python.exe main.py seedance 720p
"""

import sys
from pathlib import Path

from generation import generate
from models import Kling, Seedance, Wan
from prompt import PROMPT
from utils import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, list_files, video_duration

# ===================== SETTINGS =====================

MAX_DURATION = 20      # duration = reference video length, capped at this
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

# ====================================================


def main():
    args = [a.lower() for a in sys.argv[1:]]
    test = "--test" in args
    args = [a for a in args if a != "--test"]

    name = next((a for a in args if a in MODELS), DEFAULT_MODEL)
    resolution = next((a for a in args if a in RESOLUTIONS), DEFAULT_RESOLUTION)
    unknown = [a for a in args if a not in MODELS and a not in RESOLUTIONS]
    if unknown:
        raise SystemExit(
            f"Unknown argument: {', '.join(unknown)}. "
            f"Models: {', '.join(MODELS)} | resolutions: {', '.join(RESOLUTIONS)}"
        )
    model = MODELS[name]

    videos = list_files(IN_VIDEO, VIDEO_EXTENSIONS)
    images = list_files(IN_IMAGES, IMAGE_EXTENSIONS)
    if len(videos) != 1:
        raise SystemExit(f"{IN_VIDEO} must contain exactly 1 video (found: {len(videos)}).")
    if not images:
        raise SystemExit(f"{IN_IMAGES} contains no images.")
    video = videos[0]

    settings = model.settings(video, resolution)

    print(f"Model:      {name} ({model.endpoint})")
    print(f"Video:      {video.name} ({video_duration(video):.1f} s)")
    print(f"Parameters: {settings}")
    for i, f in enumerate(images, 1):
        print(f"Image {i}:    {f.name}")

    if test:
        print("\n--test: nothing was uploaded or generated.")
        return

    generate(model, PROMPT, video, images, settings, OUT, f"{name}_{resolution}")


if __name__ == "__main__":
    main()
