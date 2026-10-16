"""Preparing reference videos for upload: trim + compress (utils.prepare_video)."""

import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

import utils


@pytest.fixture
def ffmpeg_spy(monkeypatch):
    """Replace subprocess.run with a spy. Returns the list of recorded commands."""
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(utils.subprocess, "run", fake_run)
    return commands


@pytest.fixture
def stub_video(monkeypatch):
    """Stub duration and file size. Returns a setter."""
    def set_video(seconds, mb):
        monkeypatch.setattr(utils, "video_duration", lambda _: seconds)
        monkeypatch.setattr(utils, "file_size_mb", lambda _: mb)
    return set_video


def make_clip(path: Path, seconds: int, size: str, audio: bool = False):
    """Generate a real test clip with ffmpeg (no network), optionally with a sine tone."""
    sound = ["-f", "lavfi", "-i", f"sine=duration={seconds}", "-c:a", "aac"] if audio else []
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", f"testsrc=duration={seconds}:size={size}:rate=25",
         *sound, "-pix_fmt", "yuv420p", "-shortest", str(path)],
        check=True,
    )


@pytest.mark.parametrize("seconds, mb, expected", [
    (10, 5, False),    # short and small
    (52.6, 5, True),   # too long
    (10, 39, True),    # too big
])
def test_needs_compression(stub_video, seconds, mb, expected):
    stub_video(seconds, mb)

    assert utils.needs_compression(Path("v.mp4"), 20, 10) is expected


def test_compress_video_builds_h264_command(tmp_path, ffmpeg_spy):
    output = utils.compress_video(Path("in/clip.mov"), 20, tmp_path / "tmp")

    command = ffmpeg_spy[0]
    assert output == tmp_path / "tmp" / "clip_upload.mp4"
    assert (tmp_path / "tmp").is_dir()
    assert command[command.index("-t") + 1] == "20"
    assert command[command.index("-c:v") + 1] == "libx264"
    assert command[-1] == str(output)


def test_compress_video_muted_drops_audio(tmp_path, ffmpeg_spy):
    output = utils.compress_video(Path("clip.mp4"), 20, tmp_path, audio=False)

    command = ffmpeg_spy[0]
    assert output.name == "clip_upload_muted.mp4"
    assert "-an" in command
    assert "-c:a" not in command


def test_run_ffmpeg_error_exits(monkeypatch):
    monkeypatch.setattr(utils.subprocess, "run", lambda command, **kwargs:
                        subprocess.CompletedProcess(command, 1, "", "Invalid data"))

    with pytest.raises(SystemExit, match="Invalid data"):
        utils.run_ffmpeg(["-i", "broken.mp4"])


def test_prepare_video_keeps_small_short_video(tmp_path, stub_video, ffmpeg_spy):
    stub_video(20.0, 5)
    video = Path("short.mp4")

    assert utils.prepare_video(video, 20, 10, tmp_path) is video
    assert ffmpeg_spy == []


def test_prepare_video_compresses_long_video(tmp_path, stub_video, ffmpeg_spy):
    stub_video(52.6, 39)

    result = utils.prepare_video(Path("long.mp4"), 20, 10, tmp_path)

    assert result == tmp_path / "long_upload.mp4"
    assert len(ffmpeg_spy) == 1


def test_prepare_video_mutes_even_small_short_video(tmp_path, stub_video, ffmpeg_spy):
    stub_video(5.0, 1)

    result = utils.prepare_video(Path("short.mp4"), 20, 10, tmp_path, audio=False)

    assert result == tmp_path / "short_upload_muted.mp4"
    assert "-an" in ffmpeg_spy[0]


def test_mute_with_real_ffmpeg_keeps_original(tmp_path):
    """Integration: the uploaded copy has no audio, the original still has it."""
    source = tmp_path / "source.mp4"
    make_clip(source, 2, "320x240", audio=True)
    original_bytes = source.read_bytes()

    output = utils.compress_video(source, 2, tmp_path / "out", audio=False)

    assert utils.has_audio(source) is True
    assert utils.has_audio(output) is False
    assert source.read_bytes() == original_bytes


@pytest.mark.parametrize("source_size, expected", [
    ("1920x1080", (1280, 720)),   # landscape: long side capped
    ("1080x1920", (720, 1280)),   # vertical: long side capped
    ("320x240", (320, 240)),      # small: never upscaled
])
def test_compress_video_with_real_ffmpeg(tmp_path, source_size, expected):
    """Integration: real ffmpeg trims a 3 s clip to 1 s and scales it down."""
    source = tmp_path / "source.mp4"
    make_clip(source, 3, source_size)

    output = utils.compress_video(source, 1, tmp_path / "out")

    assert utils.video_duration(output) == pytest.approx(1.0, abs=0.1)
    assert utils.video_size(output) == expected
