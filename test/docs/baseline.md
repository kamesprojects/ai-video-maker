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
- **What it checks:** no arguments → every value comes from `config.py` (model, resolution, prompt, mute, video, images), not a test run.
- **Why:** `python main.py` must do what the config says. The test reads the expected values from `config.py`, so editing the config doesn't break it.
- **Test double:** none.

### `test_config_inputs_are_used_without_arguments`
- **What it checks:** `REFERENCE_VIDEO`, `REFERENCE_IMAGES` and `MUTE_REFERENCE_VIDEO` from `config.py` are used when no arguments are given.
- **Why:** the user can set their inputs once in the config instead of typing them every run.
- **Test double:** stubs — config values replaced with `monkeypatch`.

### `test_command_line_overrides_config`
- **What it checks:** `--video` and `--images` win over the values in `config.py`.
- **Why:** the documented rule "command line overrides config for one run".
- **Test double:** stubs — config values replaced with `monkeypatch`.

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

## `test/test_inputs.py`

Choosing the reference video and images with `--video` and `--images`.

### `test_video_and_images_options` (3 cases)
- **What it checks:** `--video X` / `--video=X` and `--images A,B` are parsed in any order; file-name case and image order are kept, spaces around commas are ignored.
- **Why:** image order decides Image 1, Image 2… in the prompt.
- **Test double:** none.

### `test_video_and_images_default_to_none`
- **What it checks:** without the options both values are `None` (= automatic choice).
- **Why:** the old behavior stays the default.
- **Test double:** none.

### `test_reference_images_in_config_accepts_text_or_list` (5 cases)
- **What it checks:** `REFERENCE_IMAGES` in `config.py` works as text (`"gazi-kiko.png"`, `"gazi, kristian"`) or a list; empty text or list means "all images".
- **Why:** writing a single name as text was read letter by letter (`'g' matches several files`).
- **Test double:** stub — config value replaced with `monkeypatch`.

### `test_option_without_value_exits` (3 cases)
- **What it checks:** `--video` without a value, `--images` followed by another flag, and `--video=` exit with "needs a value".
- **Why:** `--images --test` must not treat `--test` as an image name and skip the dry run.
- **Test double:** none.

### `test_select_file_by_name_or_stem_any_case` (4 cases)
- **What it checks:** a file is found by full name or name without extension, in any case.
- **Why:** phone videos often have upper-case extensions (`.MP4`).
- **Test double:** none (plain `Path` objects, no files needed).

### `test_select_file_by_unique_part_of_name`
- **What it checks:** `football` finds `football-video.mp4` when it is the only match.
- **Why:** shorter commands for the user.
- **Test double:** none.

### `test_select_file_ambiguous_part_exits`
- **What it checks:** a part that fits several files exits with "matches several files".
- **Why:** never guess between two videos and pay for the wrong one.
- **Test double:** none.

### `test_select_file_exact_name_wins_over_partial`
- **What it checks:** `kamil` picks `kamil.png`, not `kamil-2.png`.
- **Why:** an exact name must always be selectable even if it is part of another name.
- **Test double:** none.

### `test_select_file_unknown_lists_available`
- **What it checks:** an unknown name exits and lists the available files.
- **Why:** the user sees right away what they can choose.
- **Test double:** none.

### `test_only_video_is_used_by_default`, `test_several_videos_require_a_choice`, `test_chosen_video_among_several`, `test_no_video_exits`
- **What they check:** one video → used automatically; several → exit asking for `--video`; `--video` picks among several; empty folder → clear error.
- **Why:** with several videos the script must never pick one silently.
- **Test double:** fake folders — `IN_VIDEO` / `IN_IMAGES` point to temp folders with empty files.

### `test_all_images_sorted_by_default`, `test_chosen_images_keep_the_given_order`, `test_unknown_image_exits`, `test_no_images_exits`
- **What they check:** default = all images sorted by name (other files ignored); `--images c,a` keeps that order; unknown name and empty folder exit with a clear error.
- **Why:** the order maps people to Image 1, Image 2… in the prompt.
- **Test double:** fake folders as above.

## `test/test_settings.py`

Settings loading (`config.example.py` + personal `config.py`) and the `tmp-prompt` file.

### `test_load_uses_example_when_config_is_missing`
- **What it checks:** without `config.py`, all values come from `config.example.py`.
- **Why:** a fresh clone has no `config.py` (it is ignored by git) and must still work.
- **Test double:** fake config files written to `tmp_path`.

### `test_load_config_overrides_only_what_it_sets`
- **What it checks:** a `config.py` with one line overrides that value and keeps the rest from the example.
- **Why:** users keep only their changes; new settings added to the example later still arrive.
- **Test double:** fake config files.

### `test_load_ignores_imports_and_lowercase_names`
- **What it checks:** only UPPER_CASE names become settings (`Path` import and helpers are ignored).
- **Why:** keeps the settings namespace clean.
- **Test double:** fake config file.

### `test_real_example_defines_everything_the_code_uses`
- **What it checks:** the real `config.example.py` defines every setting the code reads.
- **Why:** a missing default would crash a fresh clone.
- **Test double:** none (reads the real file).

### `test_real_example_has_neutral_inputs`
- **What it checks:** `REFERENCE_VIDEO` and `REFERENCE_IMAGES` are `None` in the committed example.
- **Why:** personal file names belong in `config.py`, not in git.
- **Test double:** none.

### `test_tmp_prompt_is_a_selectable_name`
- **What it checks:** `tmp-prompt` is offered next to the prompts from `PROMPTS`.
- **Why:** it must work on the command line, in `--help` and in `DEFAULT_PROMPT`.
- **Test double:** none.

### `test_tmp_prompt_reads_the_file`
- **What it checks:** the text is read from `TMP_PROMPT_FILE` with surrounding whitespace removed.
- **Why:** plain text editing without Python syntax.
- **Test double:** stub — `TMP_PROMPT_FILE` points to a temp file.

### `test_tmp_prompt_missing_file_exits`, `test_tmp_prompt_empty_file_exits`
- **What they check:** a missing file exits with instructions to copy the example; an empty file exits with "is empty".
- **Why:** never send an empty prompt to a paid generation.
- **Test double:** stub — `TMP_PROMPT_FILE` points to a missing / empty temp file.

### `test_named_prompt_comes_from_prompts`
- **What it checks:** other names still return the text from `PROMPTS`.
- **Why:** `tmp-prompt` must not change how the built-in prompts work.
- **Test double:** none.

### `test_tmp_prompt_example_file_exists`
- **What it checks:** `prompts/tmp-prompt.example.txt` exists and is not empty.
- **Why:** the error message tells users to copy it.
- **Test double:** none.

## How to run

    python -m pytest -v
