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

### `test_genjutsu_sends_a_single_video_url_and_no_extra_fields`
- **What it checks:** Genjutsu gets exactly `prompt`, `video_url` (one URL, not a list), `image_urls` and `resolution`.
- **Why:** these are the documented fields (`docs/api/genjutsu-light-object-swap.md`); the other models use `video_urls`.
- **Test double:** none.

### `test_genjutsu_settings_only_resolution`
- **What it checks:** the only model setting is `resolution` (no duration, aspect ratio or audio).
- **Why:** output length follows the video; other fields are not in the schema.
- **Test double:** none.

### `test_genjutsu_uses_the_object_swap_endpoint`
- **What it checks:** the endpoint is `higgsfield/genjutsu-light/object-swap/v1.0`.
- **Why:** object swap replaces people in the video; motion transfer is a different endpoint.
- **Test double:** none.

### `test_upload_seconds` (2 cases)
- **What it checks:** Genjutsu uploads at most 15 s; a model without its own limit uses `MAX_DURATION`.
- **Why:** Genjutsu bills the input video seconds too, but only uses the first 15 s.
- **Test double:** none.

### `test_every_model_name_has_a_model`
- **What it checks:** every `ModelName` member has a model in `main.MODELS` and vice versa.
- **Why:** a name without a class (or the other way round) would crash at run time.
- **Test double:** none.

### `test_model_name_accepts_member_or_text` (3 cases), `test_unknown_model_name_exits`
- **What they check:** `parse_key(ModelName, …)` accepts `ModelName.KLING` and `"kling"`; an unknown name exits naming the config setting and the options.
- **Why:** older configs use text; a typo in `DEFAULT_MODEL` must not crash with a `KeyError`.
- **Test double:** none.

### `test_model_name_prints_as_its_value`
- **What it checks:** `ModelName.GENJUTSU_LIGHT` prints as `genjutsu-light` and equals `"wan"`-style text.
- **Why:** names appear in `--help`, `--test` and output file names.
- **Test double:** none.

### `test_too_many_images_for_genjutsu_exits`
- **What it checks:** 9 images for Genjutsu exit with "at most 8 images" before anything is uploaded.
- **Why:** the API accepts 1–8 images.
- **Test double:** none (plain `Path` objects).

## `test/test_generation.py`

### `test_completed_uploads_sends_and_downloads`
- **What it checks:** the video and images are uploaded in order, the request goes to the model endpoint with uploaded URLs, and the result is downloaded to `out/` with the right name prefix.
- **Why:** the full happy path without spending credits.
- **Test double:** fake — `fake_higgsfield()` replaces the SDK; spy — records uploads, the request and downloads; stub — `load_api_key` does nothing.

### `test_record_gets_request_id_status_and_urls`
- **What it checks:** `generate()` fills the record with the request ID, the final status, the uploaded URLs and the API response.
- **Why:** these values end up in the JSON next to the video.
- **Test double:** fake Higgsfield client; the record is a plain dict.

### `test_client_uses_long_timeout_for_uploads`
- **What it checks:** the SDK client is created with `TIMEOUT_S` (600 s), not the default 90 s.
- **Why:** with 90 s, a video upload on a slow connection failed with `httpx.WriteTimeout`.
- **Test double:** fake — `fake_higgsfield().SyncClient` records the timeout.

### `test_unsuccessful_status_exits_without_download` (NSFW, Cancelled, Failed)
- **What it checks:** each unsuccessful status exits with a matching message, does not claim success, and the record keeps the status (`nsfw`, `cancelled`, `failed`).
- **Why:** the SDK does not raise on these statuses, so the code has to check them itself.
- **Test double:** same fake client, replaying the given statuses.

### `test_api_reason_is_shown`
- **What it checks:** when the API sends an `error` (e.g. "may depict a real person"), the exit message includes it.
- **Why:** NSFW / failed responses often carry the real reason; a generic "NSFW" hid it.
- **Test double:** fake Higgsfield client returning an NSFW status with an error text.

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

### `test_every_prompt_name_has_a_text`
- **What it checks:** every `PromptName` has a text in `PROMPTS`, except `TMP_PROMPT`, which must not have one.
- **Why:** a key without a text would crash at run time; `TMP_PROMPT` is always read from its file.
- **Test double:** none.

### `test_prompt_is_returned_as_prompt_name`
- **What it checks:** `four-people` on the command line becomes `PromptName.FOUR_PEOPLE`.
- **Why:** the rest of the code works with keys, not loose text.
- **Test double:** none.

### `test_unknown_default_prompt_exits`
- **What it checks:** an unknown `DEFAULT_PROMPT` exits with "Unknown PromptName" and names the setting.
- **Why:** a typo in `config.py` must give a clear message, not a `KeyError`.
- **Test double:** stub — `DEFAULT_PROMPT` replaced with `monkeypatch`.

### `test_resolution_is_returned_as_resolution_key`
- **What it checks:** `1080P` on the command line becomes `Resolution.P1080` (any case).
- **Why:** resolutions are keys like models and prompts.
- **Test double:** none.

### `test_unknown_default_resolution_exits`
- **What it checks:** an unknown `DEFAULT_RESOLUTION` (e.g. `"4k"`) exits naming the setting and the options.
- **Why:** a typo in `config.py` must give a clear message before anything is uploaded.
- **Test double:** stub — `DEFAULT_RESOLUTION` replaced with `monkeypatch`.

### `test_default_prompt_exists`
- **What it checks:** `DEFAULT_PROMPT` is a valid `PromptName` (including `TMP_PROMPT`).
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
- **What it checks:** `REFERENCE_IMAGES` in `config.py` works as text (`"anna-photo.png"`, `"anna, ben"`) or a list; empty text or list means "all images".
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
- **What it checks:** `carl` picks `carl.png`, not `carl-2.png`.
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

### `test_describe_names_config_py_when_it_exists`, `test_describe_warns_when_only_the_example_is_used`
- **What they check:** the `Config:` line in `--test` says `config.py` when it exists, and warns "no config.py" when only the example is used.
- **Why:** editing `config.example.py` (or leaving `config.py` unsaved) looked like "the config is ignored"; the summary now shows which file is really used.
- **Test double:** fake config file in `tmp_path`.

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

## `test/test_zip_media.py`

`zip_media.py`: the media zip and `--repo` (only what git would push). The fixture creates a real throwaway git repo in `tmp_path` with ignored files (`config.py`, `.env`, media) next to normal ones.

### `test_repo_files_are_what_git_would_push`
- **What it checks:** `repo_files()` returns tracked/new files only; `config.py`, `.env` and media are left out, `.gitkeep` is kept.
- **Why:** the `--repo` zip must never contain secrets or personal files.
- **Test double:** fake repo — a real `git init` in a temp folder.

### `test_repo_files_skip_tracked_but_deleted`
- **What it checks:** a file that is tracked but deleted on disk is not listed.
- **Why:** git still lists it; zipping it would crash.
- **Test double:** fake repo.

### `test_repo_files_outside_git_exits`
- **What it checks:** outside a git repo the script exits with a clear message.
- **Why:** better than a stack trace when the project was copied without `.git`.
- **Test double:** `GIT_CEILING_DIRECTORIES` stops git from finding a parent repo.

### `test_media_files_skip_gitkeep`
- **What it checks:** the media zip includes files from `media/in` and `media/out` but not `.gitkeep`.
- **Why:** `.gitkeep` files are only placeholders for git.
- **Test double:** fake repo / temp files.

### `test_write_zip_stores_relative_paths`
- **What it checks:** paths inside the zip are relative (`in/photo.jpg`, `out/result.mp4`).
- **Why:** the zip unpacks into clean `in/` and `out/` folders.
- **Test double:** temp files.

### `test_repo_zip_contains_no_secrets_or_media`
- **What it checks:** end to end, `zip_media.py --repo` creates `zips/repo_*.zip` with code but without `config.py`, `.env` or media.
- **Why:** the guarantee the user relies on when sharing the zip.
- **Test double:** fake repo; `sys.argv` set with `monkeypatch`.

## `test/test_pricing.py`

Cost estimates (`pricing.py` + `pricing.json`) and the JSON record written by `main.run()`.

### `test_pricing_has_every_model`, `test_pricing_endpoints_match_the_models`
- **What they check:** `pricing.json` has an entry for every `ModelName`, with the same endpoint as the model class.
- **Why:** a new model without a price, or a changed endpoint, would silently give wrong estimates.
- **Test double:** none (reads the real `pricing.json`).

### `test_wan_bills_output_plus_input_seconds`
- **What it checks:** Wan 720p, 10 s output + 10 s input = $2.00.
- **Why:** Wan bills the input reference video seconds too.
- **Test double:** none.

### `test_genjutsu_rounds_output_up`
- **What it checks:** 10.2 s output is billed as 11 s; (11 + 10) × $0.05 = $1.05.
- **Why:** the Genjutsu docs say output is rounded up to whole seconds.
- **Test double:** none.

### `test_seedance_uses_video_tokens`
- **What it checks:** 720x1280, 5 s + 5 s = 216,000 tokens × $0.01284 / 1000.
- **Why:** Seedance bills by video tokens, not seconds.
- **Test double:** none.

### `test_kling_has_no_public_price`
- **What it checks:** Kling's estimate is `None` and says the price is not available.
- **Why:** never show a made-up number.
- **Test double:** none.

### `test_multiplier_applies_a_discount`
- **What it checks:** `multiplier=0.8` turns $1.00 into $0.80.
- **Why:** `PRICE_MULTIPLIER` in the config is for account discounts.
- **Test double:** none.

### `test_output_size` (3 cases)
- **What it checks:** resolution + aspect ratio → output width × height (720p 9:16 → 720x1280).
- **Why:** Seedance tokens depend on the output pixels.
- **Test double:** none.

### `test_completed_run_writes_json_with_video_and_cost`
- **What it checks:** after a completed run a JSON with the same name as the video contains status, request ID, output seconds, prompt and the cost ((10 + 10) s × $0.10 = $2.00).
- **Why:** the record the user asked for.
- **Test double:** fake `generate()`, `prepare_video()` and `video_info()` — no upload, no ffmpeg, no files.

### `test_failed_run_still_writes_json_with_zero_cost`, `test_failed_run_json_content`
- **What they check:** a failed / NSFW run still writes the JSON, with the status, the error, cost $0 and no `output`.
- **Why:** every attempt is recorded; Higgsfield doesn't charge failed requests.
- **Test double:** fake `generate()` that raises `SystemExit`.

### `test_upload_error_is_recorded_as_error`
- **What it checks:** an exception during upload is saved with status `error` and re-raised.
- **Why:** network problems are recorded too, and the user still sees the error.
- **Test double:** fake `generate()` that raises `ConnectionError`.

## `test/test_resize_videos.py`

`resize_videos.py`: downscaled copies of reference videos, never upscaled.

### `test_target_size_keeps_ratio_with_even_numbers` (3 cases)
- **What it checks:** the shorter side becomes the resolution, the ratio is kept, sizes are even (1080x1920 → 480p = 480x854).
- **Why:** H.264 needs even sizes; vertical videos must stay vertical.
- **Test double:** none.

### `test_target_size_never_upscales` (3 cases)
- **What it checks:** videos that are already that small (or smaller) get `None`.
- **Why:** upscaling only makes files bigger without more detail.
- **Test double:** none.

### `test_resized_path_and_copy_detection`
- **What it checks:** `boxing-video.MOV` → `boxing-video_480p.mp4`, and such names are recognized as copies.
- **Why:** predictable names for `--video`; copies are not resized again.
- **Test double:** none.

### `test_parse_args` (3 cases), `test_parse_args_errors` (3 cases)
- **What they check:** no argument → `RESIZE_TO`; `720P` and `--video NAME` in any order; unknown resolution, missing `--video` value and extra arguments exit with a message.
- **Why:** same rules as `main.py`: config default, command line overrides.
- **Test double:** none.

### `test_videos_to_resize_skips_earlier_copies`
- **What it checks:** "all videos" skips `*_480p.mp4` copies; `--video song` picks one.
- **Why:** running it twice must not create `x_480p_480p.mp4`.
- **Test double:** stub — `IN_VIDEO_DIR` points to a temp folder with empty files.

### `test_resize_skips_small_video_without_ffmpeg`
- **What it checks:** a small video is skipped with a message and ffmpeg is not called.
- **Why:** no needless work, the user sees why.
- **Test double:** stub — `video_size`; spy — `run_ffmpeg`.

### `test_resize_with_real_ffmpeg_keeps_original`
- **What it checks:** integration with real ffmpeg: a 1280x720 clip with sound → `clip_480p.mp4` 854x480 with sound; the original bytes are unchanged.
- **Why:** proves the real command works and never touches the original.
- **Test double:** none (clip generated with `testsrc` + `sine`, no network).

## `test/test_trim_video.py`

`trim_video.py`: cut parts of a reference video into new copies.

### `test_parse_time` (4 cases)
- **What it checks:** `8`, `2.5`, `1:05` and `0:7.5` become seconds.
- **Why:** users type times in different ways.
- **Test double:** none.

### `test_parse_range` (3 cases), `test_parse_range_errors` (5 cases)
- **What they check:** `2-8`, `2.5-8` and `1:05-1:20` are parsed (the label uses `m` instead of `:`); reversed, empty, too many parts and non-numbers exit with a message.
- **Why:** `:` is not allowed in Windows file names; a wrong range must not produce an empty or wrong clip.
- **Test double:** none.

### `test_parse_args_several_ranges_and_video`, `test_parse_args_combine_flag`, `test_parse_args_errors` (2 cases)
- **What they check:** several ranges and `--video NAME` in any order; `--combine` is off by default and on when given; no range or a missing `--video` value exit with the usage.
- **Why:** one command can cut several parts.
- **Test double:** none.

### `test_fit_to_video_shortens_the_end`, `test_fit_to_video_start_after_end_exits`
- **What they check:** a range past the end is shortened and its label (file name) shows the real end; a range that starts after the end exits.
- **Why:** the file name must match what is really in the file.
- **Test double:** none.

### `test_trimmed_path`
- **What it checks:** `boxing-video.MOV` + `2-8` → `boxing-video_2-8s.mp4` next to it.
- **Why:** predictable names for `--video` in `main.py`.
- **Test double:** none.

### `test_trim_command`
- **What it checks:** ffmpeg gets `-ss` = start and `-t` = end − start, and writes to the copy.
- **Why:** start/length are easy to mix up (`-t` is a length, not an end time).
- **Test double:** spy — `run_ffmpeg`; stubs — `video_duration`, `file_size_mb`.

### `test_main_uses_config_video`
- **What it checks:** without `--video`, `REFERENCE_VIDEO` from the config is used, and every range makes its own copy.
- **Why:** same rule as `main.py`: config default, command line overrides.
- **Test double:** stubs — `IN_VIDEO_DIR`, `REFERENCE_VIDEO`, `video_duration`; spy — `trim`.

### `test_combined_path`
- **What it checks:** `song.MP4` + `4-11`, `22-26` → `song_4-11+22-26s.mp4`.
- **Why:** the name shows which parts are inside and in what order.
- **Test double:** none.

### `test_concat_filter_with_and_without_audio`
- **What it checks:** the ffmpeg filter cuts every range (`trim` / `atrim`) and joins them with `concat`; without audio there is no `atrim` and `a=0`.
- **Why:** a video without sound would make ffmpeg fail if the filter asked for audio.
- **Test double:** none.

### `test_main_combines_only_when_asked` (3 cases)
- **What it checks:** `--combine` with 2 ranges joins them once; without it, or with only 1 range, normal copies are made.
- **Why:** separate copies stay the default; one range has nothing to join.
- **Test double:** spies — `trim`, `combine`; stubs — `IN_VIDEO_DIR`, `video_duration`.

### `test_combine_with_real_ffmpeg`
- **What it checks:** integration with real ffmpeg: 0–1 s + 2–3 s of a 4 s clip with sound → one ~2 s video with sound; the original is unchanged.
- **Why:** proves the real concat works, including audio.
- **Test double:** none (clip generated with `testsrc` + `sine`, no network).

### `test_trim_with_real_ffmpeg_keeps_original`
- **What it checks:** integration with real ffmpeg: 1–3 s of a 4 s clip with sound → a ~2 s copy with sound; the original bytes are unchanged.
- **Why:** proves the cut really works and never touches the original.
- **Test double:** none (clip generated with `testsrc` + `sine`, no network).

## How to run

    python -m pytest -v
