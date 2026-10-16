# Changelog

All notable changes to this project. Format based on [Keep a Changelog](https://keepachangelog.com/).
Every entry references its issue number, e.g. `(#1)`.

## [Unreleased]

### Added
- Reference video + images → video via the Higgsfield API (`main.py`).
- Models: Wan 3.0 reference-to-video (default), Seedance 2.5 reference-to-video, Kling O3 video-edit (`models/`).
- Model and resolution selection from the command line; `--test` dry run that uploads and bills nothing.
- Automatic duration from the reference video (max 20 s) and automatic aspect ratio.
- Reference videos longer than `MAX_DURATION` (20 s) or bigger than `MAX_UPLOAD_MB` (10 MB) are automatically trimmed and compressed with ffmpeg before upload (H.264, max 1280 px; `imageio-ffmpeg`, no separate install needed).
- `--test` output shows the input video size in MB, resolution, orientation (horizontal/vertical/square) and aspect ratio.
- Selectable prompts: `PROMPTS` object in `prompt.py` with `one-person` (default, 1 person in the video) and `four-people`; choose on the command line, e.g. `python main.py four-people`. The output file name includes the prompt.
- `--help` / `-h`: prints all arguments (models, resolutions, prompts, `--test`) with defaults, input/output folders and examples. Generated from the settings, so new models and prompts appear automatically.
- `--mute`: uploads the reference video without its audio track; the original in `media/in/` is not changed. `--test` shows an `Audio:` line (sent / removed / none).
- Handling of failed, cancelled and NSFW-moderated generations.
- `zip_media.py`: packs `media/in` and `media/out` into one zip.
- Test suite in `test/` with test doubles (fake Higgsfield client, fake MP4) and docs in `test/docs/`.
- `README.md`, `VISION.md`, `CONTRIBUTING.md`, `.env.example`.

### Fixed
- Upload of large videos failed with `httpx.WriteTimeout`: the SDK's 90 s timeout is raised to 600 s and videos are compressed before upload.
