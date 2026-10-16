"""generation.generate() with a fake Higgsfield client. No network, no billing."""

import importlib
import sys

import pytest

from doubles import fake_higgsfield
from models import Kling

# the module, not the generate() function that generation/__init__ re-exports
gen = importlib.import_module("generation.generate")

COMPLETED ={"video": {"url": "https://fake.cdn/result.mp4"}}


@pytest.fixture
def run(tmp_path, monkeypatch):
    """Run generate() against a fake client. Returns (output path, fake module)."""
    monkeypatch.setattr(gen, "load_api_key", lambda: None)
    downloads = []
    monkeypatch.setattr(gen.urllib.request, "urlretrieve",
                        lambda url, path: downloads.append((url, path)))

    video = tmp_path / "ref.mp4"
    images = [tmp_path / "1.jpg", tmp_path / "2.jpg"]

    def _run(statuses, result):
        fake = fake_higgsfield(statuses, result)
        monkeypatch.setitem(sys.modules, "higgsfield_client", fake)
        fake.downloads = downloads
        output = gen.generate(Kling(), "prompt", video, images, {"mode": "pro"},
                              tmp_path / "out", "kling_1080p")
        return output, fake

    return _run


def test_completed_uploads_sends_and_downloads(run, tmp_path):
    output, fake = run(["Queued", "InProgress", "Completed"], COMPLETED)

    assert [p.name for p in fake.calls["uploads"]] == ["ref.mp4", "1.jpg", "2.jpg"]
    assert fake.calls["subscribe"]["endpoint"] == "kling-video/o3/video-edit"
    assert fake.calls["subscribe"]["arguments"]["video_urls"] == ["https://fake.cdn/ref.mp4"]
    assert fake.downloads == [("https://fake.cdn/result.mp4", output)]
    assert output.parent == tmp_path / "out"
    assert output.name.startswith("kling_1080p_")


def test_client_uses_long_timeout_for_uploads(run):
    _, fake = run(["Completed"], COMPLETED)

    assert fake.calls["timeout"] == gen.TIMEOUT_S > 90


@pytest.mark.parametrize("status, message", [
    ("NSFW", "moderation"),
    ("Cancelled", "cancelled"),
    ("Failed", "failed"),
])
def test_unsuccessful_status_exits_without_download(run, status, message):
    with pytest.raises(SystemExit, match=message):
        run(["Queued", status], {})


def test_missing_video_url_exits(run):
    with pytest.raises(SystemExit, match="No video URL"):
        run(["Completed"], {"video": {}})
