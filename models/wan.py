from pathlib import Path

from choices import ModelName
from models.base import Model


class Wan(Model):
    """Alibaba Wan 3.0 – reference-to-video."""

    name = ModelName.WAN
    endpoint = "alibaba/wan-3.0/reference-to-video"
    min_seconds, max_seconds = 2, 30

    def settings(self, video: Path, resolution: str) -> dict:
        return {
            "duration": self.duration(video),
            "resolution": resolution,
            "aspect_ratio": "adaptive",  # detects the ratio from the video itself
            "generate_audio": self.audio,
        }
