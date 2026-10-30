"""trim_video.py: cut parts of a reference video into new copies."""

import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

import settings
import trim_video
import utils
from trim_video import Range


@pytest.mark.parametrize("text, seconds", [("8", 8.0), ("2.5", 2.5), ("1:05", 65.0), ("0:7.5", 7.5)])
def test_parse_time(text, seconds):
    assert trim_video.parse_time(text) == seconds


@pytest.mark.parametrize("text, expected", [
    ("2-8", Range(2.0, 8.0, "2-8")),
    ("2.5-8", Range(2.5, 8.0, "2.5-8")),
    ("1:05-1:20", Range(65.0, 80.0, "1m05-1m20")),   # ":" is not allowed in Windows file names
])
def test_parse_range(text, expected):
    assert trim_video.parse_range(text) == expected


@pytest.mark.parametrize("text, message", [
    ("8-2", "start must be before end"),
    ("5-5", "start must be before end"),
    ("2-", "Not a range"),
    ("2-8-9", "Not a range"),
    ("a-8", "Not a time: 'a'"),
])
def test_parse_range_errors(text, message):
    with pytest.raises(SystemExit, match=message):
        trim_video.parse_range(text)


def test_parse_args_several_ranges_and_video():
    ranges, video, combine = trim_video.parse_args(["2-8", "--video", "boxing", "12-15"])

    assert [r.label for r in ranges] == ["2-8", "12-15"]
    assert video == "boxing"
    assert combine is False   # separate copies by default


def test_parse_args_combine_flag():
    assert trim_video.parse_args(["--combine", "4-11", "22-26"])[2] is True


@pytest.mark.parametrize("argv, message", [([], "Usage"), (["2-8", "--video"], "needs a value")])
def test_parse_args_errors(argv, message):
    with pytest.raises(SystemExit, match=message):
        trim_video.parse_args(argv)


def test_fit_to_video_shortens_the_end(capsys):
    # the file name must say what is really in it: 5-10, not 5-30
    assert trim_video.fit_to_video(Range(5, 30, "5-30"), 10.0) == Range(5, 10.0, "5-10.0")
    assert trim_video.fit_to_video(Range(7.5, 15, "7.5-15"), 10.048).label == "7.5-10.0"
    assert "ends after the video" in capsys.readouterr().out


def test_fit_to_video_start_after_end_exits():
    with pytest.raises(SystemExit, match="only 10.0 s long"):
        trim_video.fit_to_video(Range(12, 15, "12-15"), 10.0)


def test_trimmed_path():
    assert trim_video.trimmed_path(Path("in/boxing-video.MOV"), Range(2, 8, "2-8")) == \
        Path("in/boxing-video_2-8s.mp4")


def test_trim_command(monkeypatch):
    commands = []
    monkeypatch.setattr(trim_video, "run_ffmpeg", commands.append)
    monkeypatch.setattr(trim_video, "video_duration", lambda _: 6.0)
    monkeypatch.setattr(trim_video, "file_size_mb", lambda _: 1.0)

    output = trim_video.trim(Path("boxing.mp4"), Range(2, 8, "2-8"))

    command = commands[0]
    assert command[command.index("-ss") + 1] == "2.000"   # start
    assert command[command.index("-t") + 1] == "6.000"    # length = end - start
    assert command[-1] == str(output) == "boxing_2-8s.mp4"


def test_main_uses_config_video(tmp_path, monkeypatch):
    for name in ["boxing.mp4", "song.mp4"]:
        (tmp_path / name).touch()
    trimmed = []
    monkeypatch.setattr(settings, "IN_VIDEO_DIR", tmp_path)
    monkeypatch.setattr(settings, "REFERENCE_VIDEO", "song")
    monkeypatch.setattr(trim_video, "video_duration", lambda _: 20.0)
    monkeypatch.setattr(trim_video, "trim", lambda video, cut: trimmed.append((video.name, cut.label)))
    monkeypatch.setattr("sys.argv", ["trim_video.py", "2-8", "12-15"])

    trim_video.main()

    assert trimmed == [("song.mp4", "2-8"), ("song.mp4", "12-15")]


def test_trim_with_real_ffmpeg_keeps_original(tmp_path):
    """Integration: 1-3 s of a 4 s clip with sound becomes a 2 s copy with sound."""
    source = tmp_path / "clip.mp4"
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", "testsrc=duration=4:size=320x240:rate=25",
         "-f", "lavfi", "-i", "sine=duration=4", "-c:a", "aac",
         "-pix_fmt", "yuv420p", "-shortest", str(source)],
        check=True,
    )
    original = source.read_bytes()

    output = trim_video.trim(source, Range(1, 3, "1-3"))

    assert output == tmp_path / "clip_1-3s.mp4"
    assert utils.video_duration(output) == pytest.approx(2.0, abs=0.1)
    assert utils.has_audio(output)
    assert source.read_bytes() == original


# --- --combine ---------------------------------------------------------------

def test_combined_path():
    cuts = [Range(4, 11, "4-11"), Range(22, 26, "22-26")]

    assert trim_video.combined_path(Path("in/song.MP4"), cuts) == Path("in/song_4-11+22-26s.mp4")


def test_concat_filter_with_and_without_audio():
    cuts = [Range(4, 11, "4-11"), Range(22, 26, "22-26")]

    with_audio = trim_video.concat_filter(cuts, audio=True)
    assert "trim=start=4.000:end=11.000" in with_audio
    assert "atrim=start=22.000:end=26.000" in with_audio
    assert with_audio.endswith("[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")

    without = trim_video.concat_filter(cuts, audio=False)
    assert "atrim" not in without
    assert without.endswith("[v0][v1]concat=n=2:v=1:a=0[v]")


@pytest.mark.parametrize("argv, combined", [
    (["4-11", "22-26", "--combine"], True),
    (["4-11", "22-26"], False),
    (["4-11", "--combine"], False),   # one range: nothing to join, a normal copy
])
def test_main_combines_only_when_asked(tmp_path, monkeypatch, argv, combined):
    (tmp_path / "song.mp4").touch()
    calls = []
    monkeypatch.setattr(settings, "IN_VIDEO_DIR", tmp_path)
    monkeypatch.setattr(trim_video, "video_duration", lambda _: 30.0)
    monkeypatch.setattr(trim_video, "trim", lambda video, cut: calls.append("trim"))
    monkeypatch.setattr(trim_video, "combine", lambda video, cuts: calls.append("combine"))
    monkeypatch.setattr("sys.argv", ["trim_video.py", *argv, "--video", "song"])

    trim_video.main()

    assert ("combine" in calls) is combined
    assert calls.count("combine") <= 1


def test_combine_with_real_ffmpeg(tmp_path):
    """Integration: 0-1 s + 2-3 s of a 4 s clip with sound -> one ~2 s video with sound."""
    source = tmp_path / "clip.mp4"
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", "testsrc=duration=4:size=320x240:rate=25",
         "-f", "lavfi", "-i", "sine=duration=4", "-c:a", "aac",
         "-pix_fmt", "yuv420p", "-shortest", str(source)],
        check=True,
    )
    original = source.read_bytes()

    output = trim_video.combine(source, [Range(0, 1, "0-1"), Range(2, 3, "2-3")])

    assert output == tmp_path / "clip_0-1+2-3s.mp4"
    assert utils.video_duration(output) == pytest.approx(2.0, abs=0.15)
    assert utils.has_audio(output)
    assert source.read_bytes() == original
