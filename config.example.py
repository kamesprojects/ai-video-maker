"""
Default settings (committed to git).

To change something, copy this file to config.py and edit it there:
    copy config.example.py config.py      (Mac/Linux: cp config.example.py config.py)
config.py is ignored by git. It may contain only the settings you change;
everything else comes from this file.

Command-line arguments override both for one run, e.g.
    python main.py seedance 720p --video football --images gazi,kristian
See `python main.py --help`.
"""

from pathlib import Path

# ===================== INPUTS =====================

# Reference video from IN_VIDEO_DIR. Full name, name without extension, or a
# unique part of the name. None = the only video in the folder.
REFERENCE_VIDEO = None            # e.g. "football"

# Reference images from IN_IMAGES_DIR, in this order: Image 1, Image 2...
# A list ["a", "b"] or text "a" / "a, b". None = all images, sorted by name.
REFERENCE_IMAGES = None           # e.g. ["image1", "image2"]

# ===================== GENERATION =====================

DEFAULT_MODEL = "wan"             # "wan", "seedance", "kling"
DEFAULT_RESOLUTION = "480p"       # "480p", "720p", "1080p" (kling: 480p/720p = std, 1080p = pro)
DEFAULT_PROMPT = "one-person"     # a key from PROMPTS in prompt.py, or "tmp-prompt"

GENERATE_AUDIO = False            # the model generates sound for the output (wan, seedance)
MUTE_REFERENCE_VIDEO = False      # upload the reference video without sound (same as --mute)

# ===================== UPLOAD =====================

MAX_DURATION = 20                 # seconds; longer reference videos are trimmed (also the output length)
MAX_UPLOAD_MB = 10                # bigger reference videos are compressed before upload
MAX_SIDE_PX = 1280                # longer side of the uploaded video (never upscaled)
TIMEOUT_S = 600                   # upload / API timeout in seconds (SDK default is 90)

# ===================== FILES & FOLDERS =====================

TMP_PROMPT_FILE = Path("prompts/tmp-prompt.txt")   # used by the "tmp-prompt" prompt
IN_VIDEO_DIR = Path("media/in/reference-video")
IN_IMAGES_DIR = Path("media/in/reference-images")
OUT_DIR = Path("media/out")       # generated videos
TMP_DIR = Path("media/tmp")       # compressed / muted copies of reference videos
