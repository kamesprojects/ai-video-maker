# Changelog

All notable changes to this project. Format based on [Keep a Changelog](https://keepachangelog.com/).
Every entry references its issue number, e.g. `(#1)`.

## [Unreleased]

### Added
- Reference video + images → video via the Higgsfield API (`main.py`).
- Models: Wan 3.0 reference-to-video (default), Seedance 2.5 reference-to-video, Kling O3 video-edit (`models/`).
- Model and resolution selection from the command line; `--test` dry run that uploads and bills nothing.
- Automatic duration from the reference video (max 20 s) and automatic aspect ratio.
- Handling of failed, cancelled and NSFW-moderated generations.
- `zip_media.py`: packs `media/in` and `media/out` into one zip.
- Test suite in `test/` with test doubles (fake Higgsfield client, fake MP4) and docs in `test/docs/`.
- `README.md`, `VISION.md`, `CONTRIBUTING.md`, `.env.example`.
