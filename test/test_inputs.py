"""Choosing the reference video and images (--video, --images)."""

from pathlib import Path

import pytest

import main
import settings
import utils


@pytest.fixture
def folders(tmp_path, monkeypatch):
    """Temp input folders instead of media/in. Returns a function that creates files."""
    video_dir, image_dir = tmp_path / "video", tmp_path / "images"
    monkeypatch.setattr(main, "IN_VIDEO", video_dir)
    monkeypatch.setattr(main, "IN_IMAGES", image_dir)

    def create(videos=(), images=()):
        for folder, names in ((video_dir, videos), (image_dir, images)):
            folder.mkdir(exist_ok=True)
            for name in names:
                (folder / name).touch()

    return create


# --- parsing ---------------------------------------------------------------

@pytest.mark.parametrize("argv", [
    ["--video", "Song.MP4", "--images", "b.png,a.png"],
    ["--video=Song.MP4", "--images=b.png,a.png"],
    ["--images", " b.png , a.png ", "--video", "Song.MP4"],
])
def test_video_and_images_options(argv):
    args = main.parse_args(argv)

    assert args.video == "Song.MP4"            # case kept for file names
    assert args.images == ["b.png", "a.png"]   # order kept


def test_video_and_images_default_to_none(monkeypatch):
    monkeypatch.setattr(settings, "REFERENCE_VIDEO", None)
    monkeypatch.setattr(settings, "REFERENCE_IMAGES", None)

    args = main.parse_args(["kling"])

    assert args.video is None and args.images is None


@pytest.mark.parametrize("config_value, expected", [
    ("anna-photo.png", ["anna-photo.png"]),          # a single name as text
    ("anna, ben", ["anna", "ben"]),      # comma-separated text
    (["anna", " ben "], ["anna", "ben"]),
    ([], None),                                    # empty = all images
    ("", None),
])
def test_reference_images_in_config_accepts_text_or_list(monkeypatch, config_value, expected):
    monkeypatch.setattr(settings, "REFERENCE_IMAGES", config_value)

    assert main.parse_args([]).images == expected


@pytest.mark.parametrize("argv", [["--video"], ["--images", "--test"], ["--video="]])
def test_option_without_value_exits(argv):
    with pytest.raises(SystemExit, match="needs a value"):
        main.parse_args(argv)


# --- select_file -----------------------------------------------------------

@pytest.mark.parametrize("name", ["Song.MP4", "song.mp4", "song", "SONG"])
def test_select_file_by_name_or_stem_any_case(name):
    files = [Path("a.mp4"), Path("Song.MP4")]

    assert utils.select_file(files, name, Path("in")) == Path("Song.MP4")


def test_select_file_by_unique_part_of_name():
    files = [Path("football-video.mp4"), Path("reference-video-song.MP4")]

    assert utils.select_file(files, "football", Path("in")).name == "football-video.mp4"


def test_select_file_ambiguous_part_exits():
    files = [Path("football-video.mp4"), Path("reference-video-song.MP4")]

    with pytest.raises(SystemExit, match="matches several files"):
        utils.select_file(files, "video", Path("in"))


def test_select_file_exact_name_wins_over_partial():
    files = [Path("carl.png"), Path("carl-2.png")]

    assert utils.select_file(files, "carl", Path("in")).name == "carl.png"


def test_select_file_unknown_lists_available():
    with pytest.raises(SystemExit, match="Available: a.mp4, b.mp4"):
        utils.select_file([Path("a.mp4"), Path("b.mp4")], "c", Path("in"))


# --- find_video / find_images ---------------------------------------------

def test_only_video_is_used_by_default(folders):
    folders(videos=["song.mp4"])

    assert main.find_video(None).name == "song.mp4"


def test_several_videos_require_a_choice(folders):
    folders(videos=["a.mp4", "b.mov"])

    with pytest.raises(SystemExit, match="Choose one with --video"):
        main.find_video(None)


def test_chosen_video_among_several(folders):
    folders(videos=["a.mp4", "b.mov"])

    assert main.find_video("b").name == "b.mov"


def test_no_video_exits(folders):
    folders()

    with pytest.raises(SystemExit, match="No video"):
        main.find_video(None)


def test_all_images_sorted_by_default(folders):
    folders(images=["ben.png", "carl.jpg", "notes.txt"])

    assert [p.name for p in main.find_images(None)] == ["ben.png", "carl.jpg"]


def test_chosen_images_keep_the_given_order(folders):
    folders(images=["a.png", "b.png", "c.png"])

    assert [p.name for p in main.find_images(["c", "a"])] == ["c.png", "a.png"]


def test_unknown_image_exits(folders):
    folders(images=["a.png"])

    with pytest.raises(SystemExit, match="'x' not found"):
        main.find_images(["x"])


def test_no_images_exits(folders):
    folders()

    with pytest.raises(SystemExit, match="No images"):
        main.find_images(None)
