from pathlib import Path

from choices import ModelName
from models.base import Model


class Kling(Model):
    """Kling O3 (Kling 3.0 Omni) – video-edit.

    Kling 3.0 has no reference-to-video; video-edit edits the input video
    based on the prompt and images, keeping its motion and length. It has
    no duration, resolution or audio – only a quality "mode".
    """

    name = ModelName.KLING
    endpoint = "kling-video/o3/video-edit"
    quality = {"480p": "std", "720p": "std", "1080p": "pro"}

    def settings(self, video: Path, resolution: str) -> dict:
        return {"mode": self.quality[resolution]}
