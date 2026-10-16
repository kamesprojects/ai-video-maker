from pathlib import Path

from utils import video_duration


class Model:
    """Common model base. Each model defines its own API parameters."""

    name = ""
    endpoint = ""
    min_seconds = None   # allowed duration; None = model uses the input video length
    max_seconds = None

    def __init__(self, audio: bool = False, max_duration: int = 20):
        self.audio = audio
        self.max_duration = max_duration

    def settings(self, video: Path, resolution: str) -> dict:
        """Model-specific parameters (without the prompt and file URLs)."""
        raise NotImplementedError

    def arguments(self, prompt: str, video_url: str, image_urls: list[str], settings: dict) -> dict:
        """Full arguments for higgsfield_client.subscribe()."""
        return {
            "prompt": prompt,
            "video_urls": [video_url],
            "image_urls": image_urls,
            **settings,
        }

    def duration(self, video: Path) -> int:
        """Duration from the reference video, clamped to model limits and max_duration."""
        seconds = round(video_duration(video))
        return max(self.min_seconds, min(seconds, self.max_duration, self.max_seconds))
