"""zip_media.py: media zip and --repo zip (only what git would push)."""

import subprocess
import zipfile
from pathlib import Path

import pytest

import zip_media


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A real throwaway git repo with ignored and committed files. cwd = repo."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], check=True)
    files = {
        ".gitignore": "/config.py\nmedia/**\n!media/**/\n!media/**/.gitkeep\n.env\n",
        "main.py": "print('hi')\n",
        "config.example.py": "X = 1\n",
        "config.py": "X = 2\n",                       # ignored
        ".env": "HF_KEY=secret\n",                    # ignored
        "media/in/.gitkeep": "",
        "media/in/photo.jpg": "jpg",                  # ignored
        "media/out/result.mp4": "mp4",                # ignored
    }
    for name, text in files.items():
        Path(name).parent.mkdir(parents=True, exist_ok=True)
        Path(name).write_text(text)
    return tmp_path


def test_repo_files_are_what_git_would_push(repo):
    names = {p.as_posix() for p in zip_media.repo_files()}

    assert names == {".gitignore", "main.py", "config.example.py", "media/in/.gitkeep"}


def test_repo_files_skip_tracked_but_deleted(repo):
    subprocess.run(["git", "add", "main.py"], check=True)
    Path("main.py").unlink()

    assert Path("main.py") not in zip_media.repo_files()


def test_repo_files_outside_git_exits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))

    with pytest.raises(SystemExit, match="git ls-files failed"):
        zip_media.repo_files()


def test_media_files_skip_gitkeep(repo):
    names = {p.as_posix() for p in zip_media.media_files()}

    assert names == {"media/in/photo.jpg", "media/out/result.mp4"}


def test_write_zip_stores_relative_paths(repo):
    output = zip_media.write_zip(zip_media.media_files(), Path("zips/test.zip"), Path("media"))

    assert sorted(zipfile.ZipFile(output).namelist()) == ["in/photo.jpg", "out/result.mp4"]


def test_repo_zip_contains_no_secrets_or_media(repo, monkeypatch):
    monkeypatch.setattr("sys.argv", ["zip_media.py", "--repo"])

    zip_media.main()

    [output] = Path("zips").glob("repo_*.zip")
    names = zipfile.ZipFile(output).namelist()
    assert "main.py" in names
    assert not {"config.py", ".env", "media/in/photo.jpg", "media/out/result.mp4"} & set(names)
