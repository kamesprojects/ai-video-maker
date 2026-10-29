from pathlib import Path

from choices import ModelName
from models.base import Model
from utils import closest_aspect_ratio, video_size


class Seedance(Model):
    """ByteDance Seedance 2.5 – reference-to-video."""

    name = ModelName.SEEDANCE
    endpoint = "bytedance/seedance-2.5/reference-to-video"
    min_seconds, max_seconds = 4, 30
    aspect_ratios = ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9"]  # no "adaptive"

    def settings(self, video: Path, resolution: str) -> dict:
        size = video_size(video)
        if not size:
            raise SystemExit("Could not read the video size for Seedance (aspect ratio).")
        return {
            "duration": self.duration(video),
            "resolution": resolution,
            "aspect_ratio": closest_aspect_ratio(size, self.aspect_ratios),
            "generate_audio": self.audio,
        }
