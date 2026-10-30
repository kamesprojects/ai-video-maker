"""resize_videos.py: downscaled copies of reference videos, never upscaled."""

import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

import resize_videos
import settings
import utils
from choices import Resolution


@pytest.mark.parametrize("size, resolution, expected", [
    ((1080, 1920), Resolution.P480, (480, 854)),     # vertical phone video
    ((1920, 1080), Resolution.P720, (1280, 720)),    # landscape
    ((1000, 1000), Resolution.P480, (480, 480)),     # square
])
def test_target_size_keeps_ratio_with_even_numbers(size, resolution, expected):
    assert resize_videos.target_size(size, resolution) == expected


@pytest.mark.parametrize("size", [(720, 1280), (480, 854), (320, 240)])
def test_target_size_never_upscales(size):
    assert resize_videos.target_size(size, Resolution.P720) is None


def test_resized_path_and_copy_detection():
    copy = resize_videos.resized_path(Path("in/boxing-video.MOV"), Resolution.P480)

    assert copy == Path("in/boxing-video_480p.mp4")
    assert resize_videos.is_resized_copy(copy)
    assert not resize_videos.is_resized_copy(Path("in/boxing-video.mp4"))


@pytest.mark.parametrize("argv, expected", [
    ([], (Resolution(settings.RESIZE_TO), None)),
    (["720P"], (Resolution.P720, None)),
    (["--video", "boxing", "1080p"], (Resolution.P1080, "boxing")),
])
def test_parse_args(argv, expected):
    assert resize_videos.parse_args(argv) == expected


@pytest.mark.parametrize("argv, message", [
    (["4k"], "Unknown resolution '4k'"),
    (["--video"], "needs a value"),
    (["480p", "720p"], "Too many arguments"),
])
def test_parse_args_errors(argv, message):
    with pytest.raises(SystemExit, match=message):
        resize_videos.parse_args(argv)


def test_videos_to_resize_skips_earlier_copies(tmp_path, monkeypatch):
    for name in ["boxing.mp4", "boxing_480p.mp4", "song.MOV"]:
        (tmp_path / name).touch()
    monkeypatch.setattr(settings, "IN_VIDEO_DIR", tmp_path)

    assert [v.name for v in resize_videos.videos_to_resize(None)] == ["boxing.mp4", "song.MOV"]
    assert resize_videos.videos_to_resize("song")[0].name == "song.MOV"


def test_resize_skips_small_video_without_ffmpeg(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(resize_videos, "video_size", lambda _: (480, 854))
    monkeypatch.setattr(resize_videos, "run_ffmpeg", calls.append)

    assert resize_videos.resize(Path("small.mp4"), Resolution.P720) is None
    assert calls == []
    assert "already 720p or smaller" in capsys.readouterr().out


def test_resize_with_real_ffmpeg_keeps_original(tmp_path):
    """Integration: a 1280x720 clip with sound becomes 854x480 with sound; original unchanged."""
    source = tmp_path / "clip.mp4"
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", "testsrc=duration=1:size=1280x720:rate=25",
         "-f", "lavfi", "-i", "sine=duration=1", "-c:a", "aac",
         "-pix_fmt", "yuv420p", "-shortest", str(source)],
        check=True,
    )
    original = source.read_bytes()

    output = resize_videos.resize(source, Resolution.P480)

    assert output == tmp_path / "clip_480p.mp4"
    assert utils.video_size(output) == (854, 480)
    assert utils.has_audio(output)
    assert source.read_bytes() == original
