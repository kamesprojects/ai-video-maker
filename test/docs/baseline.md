# Baseline (before issue tracking)

**Summary:** the first test suite, covering the code that existed before issue #1: shared helpers, the three model classes and the generation flow. No test talks to the network or bills credits.

## `test/test_utils.py`

### `test_list_files_filters_by_extension_and_sorts`
- **What it checks:** only allowed extensions are returned (case-insensitive), sorted by name.
- **Why:** image order decides Image 1, Image 2… in the prompt.
- **Test double:** none (real temp folder).

### `test_list_files_creates_missing_folder`
- **What it checks:** a missing input folder is created and returns an empty list.
- **Why:** a fresh clone must not crash before the user adds files.
- **Test double:** none.

### `test_video_size_reads_landscape`
- **What it checks:** width/height are read from the MP4 `tkhd` box.
- **Why:** Seedance needs the aspect ratio from the real video.
- **Test double:** fake — `fake_mp4()` builds a minimal MP4 in memory.

### `test_video_size_swaps_for_rotated_phone_video`
- **What it checks:** a rotated track (phone video) returns swapped width/height.
- **Why:** phone videos are stored landscape with a rotation matrix; without this, a vertical video would generate as 16:9.
- **Test double:** fake — `fake_mp4(rotated=True)`.

### `test_video_size_returns_none_without_video_track`
- **What it checks:** a file without a `moov` box returns `None` instead of crashing.
- **Why:** the caller shows a clear error instead of a stack trace.
- **Test double:** none (hand-written bytes).

### `test_closest_aspect_ratio` (4 cases)
- **What it checks:** 1920×1080 → 16:9, 1080×1920 → 9:16, 1000×1000 → 1:1, 2560×1080 → 21:9.
- **Why:** the wrong ratio means a paid generation with the wrong framing.
- **Test double:** none.

### `test_describe_size` (4 cases)
- **What it checks:** size is shown as `WxH, orientation, ~ratio` (horizontal / vertical / square), and `None` as "unknown size".
- **Why:** `main.py --test` prints it so the user can check the input video before a paid run.
- **Test double:** none.

### `test_load_api_key_falls_back_to_api_key`
- **What it checks:** `API_KEY` is accepted when `HF_KEY` is missing and copied to `HF_KEY`.
- **Why:** older `.env` files use `API_KEY`; the SDK only reads `HF_KEY`.
- **Test double:** environment variables via `monkeypatch`, empty temp dir instead of the real `.env`.

### `test_load_api_key_missing_exits`
- **What it checks:** no key → clean exit with a "missing" message.
- **Why:** a clear error instead of an SDK exception.
- **Test double:** same as above.

### `test_load_api_key_wrong_format_exits`
- **What it checks:** a key without `:` → exit asking for `key-id:key-secret`.
- **Why:** catches a key pasted in the wrong format before any request.
- **Test double:** same as above.

## `test/test_models.py`

### `test_wan_duration` (3 cases)
- **What it checks:** duration is rounded (10.4 → 10), capped by `max_duration` (25 → 20) and raised to the model minimum (0.6 → 2).
- **Why:** duration is billed per second; the 20 s cap is a project requirement.
- **Test double:** stub — `video_duration` returns a fixed number.

### `test_wan_settings`
- **What it checks:** Wan sends `adaptive` aspect ratio, the chosen resolution and the audio flag.
- **Why:** these are the parameters documented for Wan 3.0 reference-to-video.
- **Test double:** stub — `video_duration`.

### `test_seedance_minimum_is_4_seconds`
- **What it checks:** a 2 s video becomes 4 s for Seedance.
- **Why:** Seedance rejects durations under 4 s.
- **Test double:** stubs — `video_duration`, `video_size`.

### `test_seedance_picks_aspect_ratio_from_video`
- **What it checks:** a 1080×1920 video → `9:16`.
- **Why:** Seedance has no `adaptive` and defaults to 16:9.
- **Test double:** stubs — `video_duration`, `video_size`.

### `test_seedance_unknown_size_exits`
- **What it checks:** unreadable video size → clean exit.
- **Why:** better than guessing a ratio and paying for a wrong video.
- **Test double:** stub — `video_size` returns `None`.

### `test_kling_maps_resolution_to_mode` (3 cases)
- **What it checks:** 480p/720p → `std`, 1080p → `pro`.
- **Why:** Kling O3 video-edit has a quality mode instead of a resolution.
- **Test double:** none.

### `test_arguments_include_prompt_and_urls`
- **What it checks:** final arguments contain the prompt, `video_urls`, `image_urls` and model settings.
- **Why:** these field names are what the Higgsfield API expects.
- **Test double:** none.

## `test/test_generation.py`

### `test_completed_uploads_sends_and_downloads`
- **What it checks:** the video and images are uploaded in order, the request goes to the model endpoint with uploaded URLs, and the result is downloaded to `out/` with the right name prefix.
- **Why:** the full happy path without spending credits.
- **Test double:** fake — `fake_higgsfield()` replaces the SDK; spy — records uploads, the request and downloads; stub — `load_api_key` does nothing.

### `test_client_uses_long_timeout_for_uploads`
- **What it checks:** the SDK client is created with `TIMEOUT_S` (600 s), not the default 90 s.
- **Why:** with 90 s, a video upload on a slow connection failed with `httpx.WriteTimeout`.
- **Test double:** fake — `fake_higgsfield().SyncClient` records the timeout.

### `test_unsuccessful_status_exits_without_download` (NSFW, Cancelled, Failed)
- **What it checks:** each unsuccessful status exits with a matching message and does not claim success.
- **Why:** the SDK does not raise on these statuses, so the code has to check them itself.
- **Test double:** same fake client, replaying the given statuses.

### `test_missing_video_url_exits`
- **What it checks:** a completed response without a video URL → clean exit.
- **Why:** protects against unexpected API responses.
- **Test double:** same fake client.

## `test/test_trim.py`

Reference videos that are longer than `MAX_DURATION` (20 s) or bigger than `MAX_UPLOAD_MB` (10 MB) are re-encoded with the bundled ffmpeg (`imageio-ffmpeg`) before upload: trimmed, scaled to max 1280 px on the longer side, H.264. Reason: the APIs reject long inputs (Wan: max 30 s per clip) and big phone videos time out during upload.

### `test_needs_compression` (3 cases)
- **What it checks:** a short, small video is uploaded as is; a too-long or too-big one is compressed.
- **Why:** avoids needless re-encoding but catches both failure causes.
- **Test double:** stubs — `video_duration`, `file_size_mb`.

### `test_compress_video_builds_h264_command`
- **What it checks:** ffmpeg gets `-t <seconds>` and `-c:v libx264`, and the output is `<name>_upload.mp4` in the given folder.
- **Why:** predictable output and a codec every API accepts.
- **Test double:** spy — `subprocess.run` records the command.

### `test_run_ffmpeg_error_exits`
- **What it checks:** an ffmpeg failure exits with ffmpeg's error message.
- **Why:** a broken video must stop the run before anything is uploaded or billed.
- **Test double:** stub — `subprocess.run` returns exit code 1.

### `test_prepare_video_keeps_small_short_video`
- **What it checks:** a video within both limits is returned unchanged and ffmpeg is not called.
- **Why:** no needless work for videos that are fine.
- **Test double:** stubs — `video_duration`, `file_size_mb`; spy — `subprocess.run`.

### `test_prepare_video_compresses_long_video`
- **What it checks:** a 52.6 s, 39 MB video is compressed once into the temp folder.
- **Why:** the real case that timed out during upload.
- **Test double:** stubs — `video_duration`, `file_size_mb`; spy — `subprocess.run`.

### `test_compress_video_muted_drops_audio`
- **What it checks:** with `audio=False` ffmpeg gets `-an` and no audio codec, and the output is named `<name>_upload_muted.mp4`.
- **Why:** `--mute` must really drop the audio track; the name shows it is a muted copy.
- **Test double:** spy — `subprocess.run`.

### `test_prepare_video_mutes_even_small_short_video`
- **What it checks:** a short, small video is still processed when muting is requested.
- **Why:** without this, small videos would be uploaded with sound despite `--mute`.
- **Test double:** stubs — `video_duration`, `file_size_mb`; spy — `subprocess.run`.

### `test_mute_with_real_ffmpeg_keeps_original`
- **What it checks:** integration with real ffmpeg: a clip with a sine tone → the copy has no audio, the original still has audio and its bytes are unchanged.
- **Why:** the requirement is "mute the upload, keep the input video as it is".
- **Test double:** none (real ffmpeg, clip generated with `testsrc` + `sine`, no network).

### `test_compress_video_with_real_ffmpeg` (3 cases)
- **What it checks:** integration with the real ffmpeg: a 3 s clip is trimmed to ~1 s; 1920x1080 → 1280x720, 1080x1920 → 720x1280, 320x240 stays (no upscaling).
- **Why:** proves the command and the scale filter really work for both orientations.
- **Test double:** none (real ffmpeg, clip generated with `testsrc`, no network).

## `test/test_main.py`

Command-line arguments and prompt selection.

### `test_defaults_without_arguments`
- **What it checks:** no arguments → `wan`, `480p`, `DEFAULT_PROMPT`, not a test run.
- **Why:** `python main.py` must do the documented default.
- **Test double:** none.

### `test_arguments_in_any_order_and_case`
- **What it checks:** `FOUR-PEOPLE --test 720p seedance` is parsed correctly.
- **Why:** the README promises arguments in any order.
- **Test double:** none.

### `test_every_prompt_can_be_selected` (one case per prompt)
- **What it checks:** each key in `PROMPTS` is accepted as an argument.
- **Why:** a newly added prompt works without touching `main.py`.
- **Test double:** none.

### `test_unknown_argument_lists_the_options`
- **What it checks:** a typo exits and lists the available prompts.
- **Why:** a typo must never fall back silently to another prompt and bill a wrong video.
- **Test double:** none.

### `test_help_prints_usage_and_exits_ok` (`--help`, `-h`, `--HELP`)
- **What it checks:** each help flag prints the usage and exits with code 0, even when combined with other arguments like `--test`.
- **Why:** help must never start a run (or a paid generation) by accident.
- **Test double:** none (`capsys` captures the printed output).

### `test_help_lists_every_option`
- **What it checks:** the help mentions every model, resolution, prompt, `--test`, `--help` and marks the defaults.
- **Why:** the help is generated from the settings, so a new model or prompt must show up without editing the text.
- **Test double:** none.

### `test_mute_flag`
- **What it checks:** `--mute` (any case) sets `mute`, works with other arguments, and is off by default.
- **Why:** muting must be an explicit choice, never the default.
- **Test double:** none.

### `test_audio_summary` (3 cases)
- **What it checks:** the `Audio:` line says "sent with the video", "removed before upload (--mute)" or "none in the video".
- **Why:** the user sees in `--test` exactly what will be uploaded before paying.
- **Test double:** stub — `has_audio` returns a fixed answer.

### `test_default_prompt_exists`
- **What it checks:** `DEFAULT_PROMPT` is a key in `PROMPTS`.
- **Why:** catches renaming a prompt without updating the default.
- **Test double:** none.

### `test_option_names_do_not_overlap`
- **What it checks:** no name is both a model, a resolution and/or a prompt.
- **Why:** the same word in two lists would make the argument ambiguous.
- **Test double:** none.

### `test_prompts_reference_the_inputs` (one case per prompt)
- **What it checks:** every prompt mentions "Video 1" and "reference image".
- **Why:** the models need to know which input is the video and which are the images.
- **Test double:** none.

## How to run

    python -m pytest -v
