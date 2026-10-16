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
- `--video NAME` and `--images A,B`: choose the reference video and images (and their order) per run; names match by full name, name without extension or a unique part. Several videos can now live in the input folder.
- `config.py`: one place for all hand-editable settings (reference video/images, default model/resolution/prompt, audio, limits, timeout, folders). Command-line arguments override it per run. `DEFAULT_PROMPT` moved here from `prompt.py`.
- `tmp-prompt`: a prompt read from `prompts/tmp-prompt.txt` (plain text, not in git; template `prompts/tmp-prompt.example.txt`). `--test` shows the start of every prompt.
- Handling of failed, cancelled and NSFW-moderated generations.
- `zip_media.py`: packs `media/in` and `media/out` into one zip.
- Test suite in `test/` with test doubles (fake Higgsfield client, fake MP4) and docs in `test/docs/`.
- `README.md`, `VISION.md`, `CONTRIBUTING.md`, `.env.example`.

### Changed
- `config.py` is now personal and ignored by git. Defaults live in `config.example.py` (committed); `settings.py` merges both, so `config.py` is optional and may contain only changed values.

### Fixed
- `REFERENCE_IMAGES = "name.png"` (text instead of a list) in `config.py` was read letter by letter. Text and comma-separated text now work as well as a list.
- Upload of large videos failed with `httpx.WriteTimeout`: the SDK's 90 s timeout is raised to 600 s and videos are compressed before upload.
