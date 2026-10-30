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
- Genjutsu Light object swap (`genjutsu-light`, `higgsfield/genjutsu-light/object-swap/v1.0`): one `video_url`, 1–8 images, only the first 15 s are uploaded. API docs saved in `docs/api/`.
- `choices.py` with `ModelName`, `Resolution` and `PromptName`: everything you can choose as objects; in the config `DEFAULT_MODEL = ModelName.WAN`, `DEFAULT_RESOLUTION = Resolution.P480` and `DEFAULT_PROMPT = PromptName.ONE_PERSON` (plain text still works). An unknown default exits with the list of options. `PROMPTS` in `prompt.py` is keyed by `PromptName`.
- Per-model limits: `max_input_seconds` (upload only what the model uses) and `max_images` (checked before upload).
- `AGENTS.md` and `CLAUDE.md`: rules for AI agents, above all never to run a paid generation, only to write the command for the user.
- Approximate cost: `pricing.json` (list prices + billing rules per model, with sources) and `pricing.py`. `--test` prints `Est. cost:` before paying; `PRICE_MULTIPLIER` in the config for discounts.
- JSON record next to every output video (same name): status, request ID, model, prompt, input/uploaded/output video info, parameters, API response, estimated cost. Also written for failed, NSFW, cancelled and error runs (cost 0).
- `COMMANDS.md`: short reference of all commands and what they return. `--help` now mentions the `.json` record.
- `resize_videos.py`: downscaled copies of reference videos (`<name>_480p.mp4`), resolution from `RESIZE_TO` in the config or the command line, optional `--video`; never upscales, originals kept.
- `trim_video.py`: cuts parts of a reference video into copies (`<name>_2-8s.mp4`); ranges in seconds, decimals or minutes:seconds, several at once, optional `--video`; frame-accurate, original kept.
- `utils.QUALITY_ARGS` and `utils.find_one_video()` shared by `main.py`, `resize_videos.py` and `trim_video.py`.
- `trim_video.py --combine`: joins the cut parts in order into one video (`<name>_4-11+22-26s.mp4`); without it each part is a separate copy.
- Handling of failed, cancelled and NSFW-moderated generations.
- `zip_media.py`: packs `media/in` and `media/out` into one zip; `--repo` packs only the files git would push (no ignored files, secrets or media).
- Test suite in `test/` with test doubles (fake Higgsfield client, fake MP4) and docs in `test/docs/`.
- `README.md`, `VISION.md`, `CONTRIBUTING.md`, `.env.example`.

### Changed
- `README.md` shortened to setup + what the project offers; details live in `COMMANDS.md`, `--help`, `config.example.py` and the code.
- `config.py` is now personal and ignored by git. Defaults live in `config.example.py` (committed); `settings.py` merges both, so `config.py` is optional and may contain only changed values.

### Fixed
- NSFW / failed / cancelled runs now print the reason sent by the API (e.g. "may depict a real person") and say that nothing was charged.
- Confusing config: `--test` now prints a `Config:` line with the file the settings come from, and `config.example.py` says clearly not to edit it (values in `config.py` always win).
- `REFERENCE_IMAGES = "name.png"` (text instead of a list) in `config.py` was read letter by letter. Text and comma-separated text now work as well as a list.
- Upload of large videos failed with `httpx.WriteTimeout`: the SDK's 90 s timeout is raised to 600 s and videos are compressed before upload.
