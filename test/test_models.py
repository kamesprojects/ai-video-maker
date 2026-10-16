from pathlib import Path

import pytest

import models.base
import models.seedance
from models import Kling, Seedance, Wan

VIDEO = Path("ref.mp4")  # never opened: duration and size are stubbed


@pytest.fixture
def stub_duration(monkeypatch):
    """Stub video_duration so no real file is needed. Returns a setter."""
    def set_seconds(seconds):
        monkeypatch.setattr(models.base, "video_duration", lambda _: seconds)
    set_seconds(10.0)
    return set_seconds


@pytest.mark.parametrize("seconds, expected", [
    (10.4, 10),   # rounded
    (25.0, 20),   # capped by max_duration
    (0.6, 2),     # raised to the model minimum
])
def test_wan_duration(stub_duration, seconds, expected):
    stub_duration(seconds)

    assert Wan(max_duration=20).settings(VIDEO, "480p")["duration"] == expected


def test_wan_settings(stub_duration):
    settings = Wan(audio=True).settings(VIDEO, "720p")

    assert settings == {
        "duration": 10, "resolution": "720p",
        "aspect_ratio": "adaptive", "generate_audio": True,
    }


def test_seedance_minimum_is_4_seconds(stub_duration, monkeypatch):
    stub_duration(2.0)
    monkeypatch.setattr(models.seedance, "video_size", lambda _: (1920, 1080))

    assert Seedance().settings(VIDEO, "480p")["duration"] == 4


def test_seedance_picks_aspect_ratio_from_video(stub_duration, monkeypatch):
    monkeypatch.setattr(models.seedance, "video_size", lambda _: (1080, 1920))

    assert Seedance().settings(VIDEO, "480p")["aspect_ratio"] == "9:16"


def test_seedance_unknown_size_exits(stub_duration, monkeypatch):
    monkeypatch.setattr(models.seedance, "video_size", lambda _: None)

    with pytest.raises(SystemExit):
        Seedance().settings(VIDEO, "480p")


@pytest.mark.parametrize("resolution, mode", [("480p", "std"), ("720p", "std"), ("1080p", "pro")])
def test_kling_maps_resolution_to_mode(resolution, mode):
    assert Kling().settings(VIDEO, resolution) == {"mode": mode}


def test_arguments_include_prompt_and_urls():
    args = Kling().arguments("prompt", "https://v", ["https://i1"], {"mode": "pro"})

    assert args == {
        "prompt": "prompt", "video_urls": ["https://v"],
        "image_urls": ["https://i1"], "mode": "pro",
    }
