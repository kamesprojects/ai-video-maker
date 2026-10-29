from pathlib import Path

from choices import ModelName
from models.base import Model


class GenjutsuLight(Model):
    """Higgsfield Genjutsu Light – object swap (docs: docs/api/genjutsu-light-object-swap.md).

    Replaces objects, characters or clothes in the reference video using the
    reference images. Uses only the first 15 s of the video, keeps its audio,
    output length follows the video. Billed per second of output + input video.
    """

    name = ModelName.GENJUTSU_LIGHT
    endpoint = "higgsfield/genjutsu-light/object-swap/v1.0"
    max_input_seconds = 15   # the rest would be billed but never used
    max_images = 8

    def settings(self, video: Path, resolution: str) -> dict:
        return {"resolution": resolution}

    def arguments(self, prompt: str, video_url: str, image_urls: list[str], settings: dict) -> dict:
        # one video_url (not a list like the other models)
        return {"prompt": prompt, "video_url": video_url, "image_urls": image_urls, **settings}
