# AI Video Maker (Higgsfield API)

Replaces the people in a reference video with the people from reference images. Supports Wan 3.0 (default), Seedance 2.5 and Kling O3.

## Setup (after cloning from GitHub)

Requirements: **Python 3.10+** and a [Higgsfield](https://console.higgsfield.ai) account with credits.

**1. Clone the repo**
```powershell
git clone <repo-url>
cd ai-video-maker
```

**2. Create a virtual environment and install dependencies**

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
Mac/Linux:
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**3. Add your API key**

Create an API key at [console.higgsfield.ai](https://console.higgsfield.ai) → API keys. Then copy the example file:
```powershell
copy .env.example .env      # Mac/Linux: cp .env.example .env
```
Open `.env` and replace the placeholder with your key in `key-id:key-secret` format:
```
HF_KEY=your-key-id:your-key-secret
```
`.env` is ignored by git, so never commit or share it.

**4. (Optional) Your own settings and scratch prompt**
```powershell
copy config.example.py config.py                             # Mac/Linux: cp
copy prompts\tmp-prompt.example.txt prompts\tmp-prompt.txt   # Mac/Linux: cp prompts/...
```
Both copies are ignored by git. Without `config.py` the defaults from `config.example.py` are used.

**5. Add your inputs**
- video(s) → `media/in/reference-video/`
- images of the people → `media/in/reference-images/`

**6. Check that everything works (free)**
```powershell
.\.venv\Scripts\python.exe main.py --test      # Mac/Linux: .venv/bin/python main.py --test
```

## Can I run a generation?

**Yes.** You run generations yourself once these conditions are met:

1. `.venv` is installed and `.env` contains your key (see Setup).
2. `media/in/reference-video/` contains a video (if there are several, choose one with `--video`).
3. `media/in/reference-images/` contains at least 1 image.
4. You have credits on Higgsfield.

⚠️ Every generation is **paid** (billed per second of video). Always check it first with `--test`, which uploads nothing and costs nothing.

## How to run a generation

```powershell
# all arguments, defaults and examples
.\.venv\Scripts\python.exe main.py --help

# 1) free check: prints the model, prompt, video, images and parameters
.\.venv\Scripts\python.exe main.py --test

# 2) if everything looks right, run the generation
.\.venv\Scripts\python.exe main.py                            # wan, 480p, one-person
.\.venv\Scripts\python.exe main.py seedance 720p
.\.venv\Scripts\python.exe main.py kling 1080p four-people
.\.venv\Scripts\python.exe main.py --mute                     # reference video sent without sound
```

Arguments can be in any order. Anything you leave out uses the default.

A generation takes a few minutes. The script prints the status (`Queued` → `InProgress` → `Completed`) and saves the video to `media/out/` at the end. If the API rejects it (NSFW), cancels it, or it fails, the script says so and exits.

- **Model:** `wan` (default), `seedance`, `kling`
- **Resolution:** `480p` (default), `720p`, `1080p`
- **Prompt:** `one-person` (default), `four-people` (see [Prompts](#prompts))
- **`--mute`:** upload the reference video **without sound**. Only the uploaded copy in `media/tmp/` is muted, your original in `media/in/` keeps its audio. Without `--mute` the sound is sent along. `--test` shows which one will happen (`Audio:` line). Muted runs get `_muted` in the output file name.
  This is different from `AUDIO` in `main.py`, which decides whether the model **generates** sound for the output video.
- **Duration:** automatic, from the reference video (rounded to whole seconds), max 20 s.
- **Long or big videos:** a reference video longer than 20 s or bigger than 10 MB is automatically trimmed to its first 20 s and compressed (H.264, max 1280 px) before upload, e.g. 100 MB → 3 MB. The copy goes to `media/tmp/`, the original is not changed. `--test` shows when this will happen.
- **Aspect ratio:** automatic, from the video.

**Kling:** Kling 3.0 has no reference-to-video, so the project uses **Kling O3 Video Edit**. It edits the input video, so the output has the same length as the (trimmed) input. Instead of a resolution it has a quality mode: `480p`/`720p` = `std`, `1080p` = `pro`. No audio.

## Configuration (`config.py`)

- [`config.example.py`](config.example.py) holds the **defaults** and is committed to git.
- `config.py` holds **your** settings and is **ignored by git**, so your file names and choices stay private. Create it with `copy config.example.py config.py`. It may contain only the lines you change; everything else comes from `config.example.py`.
- [`settings.py`](settings.py) merges the two; the code always reads from it.

Available settings:

| Setting | Default | Meaning |
|---|---|---|
| `REFERENCE_VIDEO` | `None` | which video to use (`None` = the only one in the folder) |
| `REFERENCE_IMAGES` | `None` | which images, in order: a list `["gazi", "kristian"]` or text `"gazi"` / `"gazi, kristian"` (`None` = all, sorted by name) |
| `DEFAULT_MODEL` | `"wan"` | `wan`, `seedance`, `kling` |
| `DEFAULT_RESOLUTION` | `"480p"` | `480p`, `720p`, `1080p` |
| `DEFAULT_PROMPT` | `"one-person"` | a key from `PROMPTS` in `prompt.py`, or `"tmp-prompt"` |
| `GENERATE_AUDIO` | `False` | the model generates sound for the output (wan, seedance) |
| `MUTE_REFERENCE_VIDEO` | `False` | upload the reference video without sound (same as `--mute`) |
| `MAX_DURATION` | `20` | seconds; longer reference videos are trimmed, also the output length |
| `MAX_UPLOAD_MB` | `10` | bigger reference videos are compressed before upload |
| `MAX_SIDE_PX` | `1280` | longer side of the uploaded video |
| `TIMEOUT_S` | `600` | upload / API timeout in seconds |
| `TMP_PROMPT_FILE` | `prompts/tmp-prompt.txt` | text file used by the `tmp-prompt` prompt |
| `IN_VIDEO_DIR`, `IN_IMAGES_DIR`, `OUT_DIR`, `TMP_DIR` | `media/...` | input, output and temp folders |

**Command-line arguments override the config for one run.** For example, with `REFERENCE_VIDEO = "football"` in the config, `python main.py --video song` uses `song` this time. `--help` and `--test` always show the values that will really be used.

## Choosing the video and images

You can keep several videos and many photos in the input folders and pick per run:

```powershell
.\.venv\Scripts\python.exe main.py --video football --images gazi,kristian --test
```

- **`--video NAME`:** which video from `media/in/reference-video/` to use. Without it, the only video in the folder is used; with several videos the script asks you to choose.
- **`--images A,B,…`:** which photos from `media/in/reference-images/` to use, **in this order**: the first is Image 1, the second Image 2… Without it, all photos are used, sorted by name.
- **Names:** you can write the full name (`football-video.mp4`), the name without extension (`football-video`) or just a part that fits only one file (`football`). Upper/lower case doesn't matter. If the name fits no file or several files, the script lists what is available.
- `--video=NAME` and `--images=A,B` also work.
- `--test` prints the chosen video and `Image 1`, `Image 2`… so you can check the order before paying.

## Prompts

Prompts live in [`prompt.py`](prompt.py) in the `PROMPTS` object. Pick the one that matches your **reference video**:

| Prompt | Use when | Reference images |
|---|---|---|
| `one-person` (default) | the video shows **1 person** and you want to replace them | 1 or more photos of the **same** person. More photos from different angles (front, side, smiling) give a better face match. |
| `four-people` | the video shows **4 people** side by side | exactly 4 photos, one per person. Sorted by file name: the 1st file replaces the 1st person from the left, and so on. Name them `1_….jpg`, `2_….jpg`… to control the order. |

```powershell
.\.venv\Scripts\python.exe main.py one-person --test     # check first
.\.venv\Scripts\python.exe main.py one-person            # generate
```

Tips for good results:
- Use clear, well-lit photos where the face is fully visible (no sunglasses, no heavy filters).
- Describe **what to keep** (motion, background, camera), not what the person looks like. The look comes from the images.

**Trying a prompt quickly (`tmp-prompt`):** write plain text (no Python, no quotes) into `prompts/tmp-prompt.txt` and run:
```powershell
.\.venv\Scripts\python.exe main.py tmp-prompt --test     # shows the start of the text
.\.venv\Scripts\python.exe main.py tmp-prompt
```
The file is ignored by git; `prompts/tmp-prompt.example.txt` is the committed template. To use it by default, set `DEFAULT_PROMPT = "tmp-prompt"` in `config.py`. If the file is missing or empty, the script stops instead of sending an empty prompt.

**Adding your own prompt:** add a new entry to `PROMPTS` in `prompt.py`, e.g. `"two-people": """..."""`. The key is the name you type on the command line. It must not clash with a model or resolution name (a test checks this). Refer to the inputs as "Video 1" and "Image 1", "Image 2"… To change the default, set `DEFAULT_PROMPT` in `config.py`.

## Zip inputs and outputs

Packs `media/in` and `media/out` into one zip (with `in/` and `out/` folders inside), e.g. for sharing or backup:
```powershell
.\.venv\Scripts\python.exe zip_media.py
```
The zip is saved to `zips/media_<date>.zip`. The `zips/` folder is ignored by git.

## Folders

| Folder / file | Contents |
|---|---|
| `media/in/reference-video/` | reference videos (`.mp4`, `.mov`). One is used automatically; with several, choose with `--video` |
| `media/in/reference-images/` | images of the people (`.jpg`, `.png`, `.webp`). By default all of them, sorted by name; choose which and in what order with `--images` |
| `media/out/` | finished videos (`model_resolution_prompt_date.mp4`) |
| `prompt.py` | the prompts (`PROMPTS` object) |
| `prompts/` | `tmp-prompt.txt` (your scratch prompt, not in git) and `tmp-prompt.example.txt` |
| `config.example.py` | default settings (in git) |
| `config.py` | **your settings** (not in git), see [Configuration](#configuration-configpy) |
| `settings.py` | merges `config.example.py` + `config.py`; the code reads settings from here |
| `main.py` | the entry point (command line, summary, run) |
| `models/` | one class per model (`wan.py`, `seedance.py`, `kling.py`) defining its API parameters |
| `generation/` | the generation itself: upload, request, wait, download |
| `utils.py` | shared helpers (files, video duration and size, API key) |
| `zip_media.py` | packs `media/in` + `media/out` into one zip in `zips/` |
| `test/` | tests (`doubles.py` = shared fakes/stubs) and `test/docs/` = test documentation per issue |

Everything inside `media/` (your photos and videos) stays local and is not committed. Only the empty folder structure is in the repo.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt   # once
.\.venv\Scripts\python.exe -m pytest -v
```
Tests use test doubles and never call the real API or bill credits. Test documentation is in [`test/docs/`](test/docs/).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the rules (AI use, tests, changelog), [`VISION.md`](VISION.md) for where the project is going and [`CHANGELOG.md`](CHANGELOG.md) for what changed.

## Adding a new model

1. Create `models/new_model.py` with a class that inherits from `Model` and sets `endpoint` and `settings()`.
2. Add it to `models/__init__.py`.
3. Add it to `MODELS` in `main.py`.
