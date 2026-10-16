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

### `test_unsuccessful_status_exits_without_download` (NSFW, Cancelled, Failed)
- **What it checks:** each unsuccessful status exits with a matching message and does not claim success.
- **Why:** the SDK does not raise on these statuses, so the code has to check them itself.
- **Test double:** same fake client, replaying the given statuses.

### `test_missing_video_url_exits`
- **What it checks:** a completed response without a video URL → clean exit.
- **Why:** protects against unexpected API responses.
- **Test double:** same fake client.

## How to run

    python -m pytest -v
