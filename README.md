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

- **Model:** `wan` (default), `seedance`, `kling`, `genjutsu-light`
- **Resolution:** `480p` (default), `720p`, `1080p`
- **Prompt:** `one-person` (default), `four-people` (see [Prompts](#prompts))
- **`--mute`:** upload the reference video **without sound**. Only the uploaded copy in `media/tmp/` is muted, your original in `media/in/` keeps its audio. Without `--mute` the sound is sent along. `--test` shows which one will happen (`Audio:` line). Muted runs get `_muted` in the output file name.
  This is different from `AUDIO` in `main.py`, which decides whether the model **generates** sound for the output video.
- **Duration:** automatic, from the reference video (rounded to whole seconds), max 20 s.
- **Long or big videos:** a reference video longer than 20 s or bigger than 10 MB is automatically trimmed to its first 20 s and compressed (H.264, max 1280 px) before upload, e.g. 100 MB → 3 MB. The copy goes to `media/tmp/`, the original is not changed. `--test` shows when this will happen.
- **Aspect ratio:** automatic, from the video.

**Genjutsu Light:** Higgsfield's own **object swap** model (`higgsfield/genjutsu-light/object-swap/v1.0`, docs in [`docs/api/`](docs/api/genjutsu-light-object-swap.md)). It replaces characters, objects or clothes in the video with the ones from the images (1–8 images), keeps the video's audio and length. It uses only the first 15 s, so the script uploads at most 15 s. ⚠️ It is billed per second of **output + input video** (480p $0.05/s, 720p $0.10/s, 1080p $0.20/s), so a 15 s video costs about 30 billed seconds.

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
| `DEFAULT_MODEL` | `ModelName.WAN` | `ModelName.WAN` / `SEEDANCE` / `KLING` / `GENJUTSU_LIGHT` (from `choices.py`; plain text like `"wan"` also works) |
| `DEFAULT_RESOLUTION` | `Resolution.P480` | `Resolution.P480` / `P720` / `P1080` (from `choices.py`; plain text also works) |
| `DEFAULT_PROMPT` | `PromptName.ONE_PERSON` | `PromptName.ONE_PERSON` / `FOUR_PEOPLE` / `TMP_PROMPT` (from `choices.py`; plain text also works) |
| `GENERATE_AUDIO` | `False` | the model generates sound for the output (wan, seedance) |
| `MUTE_REFERENCE_VIDEO` | `False` | upload the reference video without sound (same as `--mute`) |
| `MAX_DURATION` | `20` | seconds; longer reference videos are trimmed, also the output length |
| `MAX_UPLOAD_MB` | `10` | bigger reference videos are compressed before upload |
| `MAX_SIDE_PX` | `1280` | longer side of the uploaded video |
| `TIMEOUT_S` | `600` | upload / API timeout in seconds |
| `PRICE_MULTIPLIER` | `1.0` | applied to cost estimates, e.g. `0.8` if you have a 20 % discount |
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

**Adding your own prompt:**
1. Add a key to `PromptName` in [`choices.py`](choices.py), e.g. `BOXING = "boxing"`. The value is the name you type on the command line; it must not clash with a model or resolution name (a test checks this).
2. Add its text to `PROMPTS` in `prompt.py`: `PromptName.BOXING: """..."""`. Refer to the inputs as "Video 1" and "Image 1", "Image 2"… (the model doesn't see file names).
3. Run it with `python main.py boxing`, or set `DEFAULT_PROMPT = PromptName.BOXING` in `config.py`.

A test checks that every `PromptName` has a text (except `TMP_PROMPT`, which comes from the file).

## Cost estimate and JSON record

**Before paying:** `--test` prints an approximate cost, e.g.
```
Est. cost:  ~$2.10 (11.0 s output + 10.0 s input x $0.1/s)
```

**After a run:** next to every video in `media/out/` a JSON file with the same name is saved, e.g. `genjutsu-light_720p_tmp-prompt_20261029_143000.mp4` + `.json`. It contains:
- `status`, `request_id`, start and finish time
- model and endpoint, prompt name and full text
- input video (original and uploaded copy: seconds, MB, resolution), images in order, muted or not
- parameters sent to the API, uploaded URLs and the API response
- output video (seconds, MB, resolution)
- `estimated_cost_before` (from `--test`) and `cost` (with the real output length)

A JSON is written **also when a generation fails** (status `failed` / `nsfw` / `cancelled` / `error`, with the error and cost `0`, because Higgsfield doesn't charge those).

**Prices** come from [`pricing.json`](pricing.json): list prices from the Higgsfield model docs (with the source link and the date they were checked). The API itself doesn't return a cost, so every number is **approximate** and before discounts; set `PRICE_MULTIPLIER` in `config.py` for a discount. Kling O3 has no public price, so its cost is shown as unknown. Exact charges are in the [Higgsfield console](https://console.higgsfield.ai).

| Model | Billing |
|---|---|
| `wan`, `genjutsu-light` | (output + input video seconds) × 480p $0.05 / 720p $0.10 / 1080p $0.20 per second |
| `seedance` | video tokens = width × height × (output + input seconds) × 24 / 1024, × $0.01284 (480p/720p) or $0.01404 (1080p) per 1000 |
| `kling` | no public price |

## Zip files

```powershell
.\.venv\Scripts\python.exe zip_media.py          # media/in + media/out  -> zips/media_<date>.zip
.\.venv\Scripts\python.exe zip_media.py --repo   # what git would push   -> zips/repo_<date>.zip
```

- **Without a flag:** packs `media/in` and `media/out` (with `in/` and `out/` folders inside), e.g. for sharing results or a backup. `.gitkeep` files are skipped.
- **`--repo`:** packs exactly the files git would commit and push: tracked files plus new ones, **without** anything in `.gitignore`. So no `.env`, `config.py`, `prompts/tmp-prompt.txt`, `.venv/`, media or zips. Useful for sending the project to someone without GitHub. Uses `git ls-files`, so git must be installed.

The `zips/` folder is ignored by git.

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
| `models/` | one class per model (`wan.py`, `seedance.py`, `kling.py`, `genjutsu.py`) defining its API parameters |
| `choices.py` | `ModelName`, `Resolution`, `PromptName`: everything you can choose, used in `config.py` |
| `docs/api/` | copies of the Higgsfield API docs for our models |
| `AGENTS.md`, `CLAUDE.md` | rules for AI coding agents (e.g. never run a paid generation) |
| `generation/` | the generation itself: upload, request, wait, download |
| `utils.py` | shared helpers (files, video duration and size, API key) |
| `pricing.json`, `pricing.py` | model prices and the cost estimate |
| `zip_media.py` | zips `media/in` + `media/out`, or with `--repo` the files git would push, into `zips/` |
| `test/` | tests (`doubles.py` = shared fakes/stubs) and `test/docs/` = test documentation per issue |

Everything inside `media/` (your photos and videos) stays local and is not committed. Only the empty folder structure is in the repo.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt   # once
.\.venv\Scripts\python.exe -m pytest -v
```
Tests use test doubles and never call the real API or bill credits. Test documentation is in [`test/docs/`](test/docs/).

## Contributing

AI agents: read [`AGENTS.md`](AGENTS.md) first.


See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the rules (AI use, tests, changelog), [`VISION.md`](VISION.md) for where the project is going and [`CHANGELOG.md`](CHANGELOG.md) for what changed.

## Adding a new model

1. Add its key to `ModelName` in `choices.py`.
2. Create `models/new_model.py` with a class that inherits from `Model` and sets `name`, `endpoint` and `settings()` (override `arguments()` if the API uses different field names).
3. Add it to `models/__init__.py` and to the `MODELS` list in `main.py`.
4. Save its API docs to `docs/api/`.
