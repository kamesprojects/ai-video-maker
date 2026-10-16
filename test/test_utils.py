import pytest

import utils
from doubles import fake_mp4


def test_list_files_filters_by_extension_and_sorts(tmp_path):
    for name in ["b.jpg", "a.png", "notes.txt", "c.JPG"]:
        (tmp_path / name).touch()

    result = utils.list_files(tmp_path, utils.IMAGE_EXTENSIONS)

    assert [p.name for p in result] == ["a.png", "b.jpg", "c.JPG"]


def test_list_files_creates_missing_folder(tmp_path):
    folder = tmp_path / "missing"

    assert utils.list_files(folder, utils.IMAGE_EXTENSIONS) == []
    assert folder.is_dir()


def test_video_size_reads_landscape(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(fake_mp4(1280, 720))

    assert utils.video_size(video) == (1280, 720)


def test_video_size_swaps_for_rotated_phone_video(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(fake_mp4(1920, 1080, rotated=True))

    assert utils.video_size(video) == (1080, 1920)


def test_video_size_returns_none_without_video_track(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"\x00\x00\x00\x0cftypisom")

    assert utils.video_size(video) is None


@pytest.mark.parametrize("size, expected", [
    ((1920, 1080), "16:9"),
    ((1080, 1920), "9:16"),
    ((1000, 1000), "1:1"),
    ((2560, 1080), "21:9"),
])
def test_closest_aspect_ratio(size, expected):
    ratios = ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9"]

    assert utils.closest_aspect_ratio(size, ratios) == expected


@pytest.mark.parametrize("size, expected", [
    ((1920, 1080), "1920x1080, horizontal, ~16:9"),
    ((1080, 1920), "1080x1920, vertical, ~9:16"),
    ((720, 720), "720x720, square, ~1:1"),
    (None, "unknown size"),
])
def test_describe_size(size, expected):
    assert utils.describe_size(size) == expected


@pytest.fixture
def clean_env(tmp_path, monkeypatch):
    """Empty working dir (no .env) and no key variables."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HF_KEY", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)


def test_load_api_key_falls_back_to_api_key(clean_env, monkeypatch):
    import os
    monkeypatch.setenv("API_KEY", "id:secret")

    utils.load_api_key()

    assert os.environ["HF_KEY"] == "id:secret"


def test_load_api_key_missing_exits(clean_env):
    with pytest.raises(SystemExit, match="missing"):
        utils.load_api_key()


def test_load_api_key_wrong_format_exits(clean_env, monkeypatch):
    monkeypatch.setenv("HF_KEY", "no-colon")

    with pytest.raises(SystemExit, match="key-id:key-secret"):
        utils.load_api_key()
