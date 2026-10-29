"""
Pack files into one zip in zips/.

    .venv\\Scripts\\python.exe zip_media.py          # media/in + media/out -> zips/media_<date>.zip
    .venv\\Scripts\\python.exe zip_media.py --repo   # what git would push    -> zips/repo_<date>.zip
"""

import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

MEDIA = Path("media")
FOLDERS = ["in", "out"]
ZIP_DIR = Path("zips")


def media_files() -> list[Path]:
    """All files in media/in and media/out, without .gitkeep."""
    return [
        f
        for folder in FOLDERS
        for f in sorted((MEDIA / folder).rglob("*"))
        if f.is_file() and f.name != ".gitkeep"
    ]


def repo_files() -> list[Path]:
    """Files git would commit: tracked + new, without anything in .gitignore."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"git ls-files failed (is git installed and is this a repo?): {error}")
    # deleted-but-tracked files are still listed by git, skip them
    return [Path(line) for line in sorted(result.stdout.splitlines()) if Path(line).is_file()]


def write_zip(files: list[Path], output: Path, base: Path = Path(".")) -> Path:
    """Zip `files` with paths relative to `base`."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, f.relative_to(base))
            print(f"Added {f.relative_to(base).as_posix()}")
    print(f"\nSaved {output} ({len(files)} files, {output.stat().st_size / 1_000_000:.1f} MB)")
    return output


def main():
    repo = "--repo" in sys.argv[1:]
    files = repo_files() if repo else media_files()
    if not files:
        raise SystemExit("Nothing to zip." if repo else
                         f"Nothing to zip: {MEDIA}/in and {MEDIA}/out are empty.")

    output = ZIP_DIR / f"{'repo' if repo else 'media'}_{datetime.now():%Y%m%d_%H%M%S}.zip"
    write_zip(files, output, Path(".") if repo else MEDIA)


if __name__ == "__main__":
    main()
