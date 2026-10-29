from pathlib import Path

from utils import video_duration


class Model:
    """Common model base. Each model defines its own API parameters."""

    name = None          # a ModelName
    endpoint = ""
    min_seconds = None   # allowed duration; None = model uses the input video length
    max_seconds = None
    max_input_seconds = None   # the model only uses this much of the reference video
    max_images = None          # most reference images the API accepts

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

    def upload_seconds(self, max_duration: int) -> int:
        """How much of the reference video to upload (the rest is never used)."""
        return min(max_duration, self.max_input_seconds or max_duration)

    def duration(self, video: Path) -> int:
        """Duration from the reference video, clamped to model limits and max_duration."""
        seconds = round(video_duration(video))
        return max(self.min_seconds, min(seconds, self.max_duration, self.max_seconds))
