"""
Pack media/in and media/out into one zip file (zips/media_<date>.zip).

    .venv\\Scripts\\python.exe zip_media.py
"""

import zipfile
from datetime import datetime
from pathlib import Path

MEDIA = Path("media")
FOLDERS = ["in", "out"]
ZIP_DIR = Path("zips")


def main():
    files = [
        f
        for folder in FOLDERS
        for f in sorted((MEDIA / folder).rglob("*"))
        if f.is_file() and f.name != ".gitkeep"
    ]
    if not files:
        raise SystemExit(f"Nothing to zip: {MEDIA}/in and {MEDIA}/out are empty.")

    ZIP_DIR.mkdir(exist_ok=True)
    output = ZIP_DIR / f"media_{datetime.now():%Y%m%d_%H%M%S}.zip"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, f.relative_to(MEDIA))  # stored as in/... and out/...
            print(f"Added {f.relative_to(MEDIA)}")

    print(f"\nSaved {output} ({len(files)} files, {output.stat().st_size / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    main()
