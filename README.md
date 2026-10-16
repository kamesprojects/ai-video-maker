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

**4. Add your inputs**
- 1 video → `media/in/reference-video/`
- images of the people → `media/in/reference-images/`

**5. Check that everything works (free)**
```powershell
.\.venv\Scripts\python.exe main.py --test      # Mac/Linux: .venv/bin/python main.py --test
```

## Can I run a generation?

**Yes.** You run generations yourself once these conditions are met:

1. `.venv` is installed and `.env` contains your key (see Setup).
2. `media/in/reference-video/` contains **exactly 1** video.
3. `media/in/reference-images/` contains at least 1 image.
4. You have credits on Higgsfield.

⚠️ Every generation is **paid** (billed per second of video). Always check it first with `--test`, which uploads nothing and costs nothing.

## How to run a generation

```powershell
# 1) free check: prints the model, video, images and parameters
.\.venv\Scripts\python.exe main.py --test

# 2) if everything looks right, run the generation
.\.venv\Scripts\python.exe main.py                    # wan, 480p
.\.venv\Scripts\python.exe main.py seedance 720p
.\.venv\Scripts\python.exe main.py kling 1080p
```

A generation takes a few minutes. The script prints the status (`Queued` → `InProgress` → `Completed`) and saves the video to `media/out/` at the end. If the API rejects it (NSFW), cancels it, or it fails, the script says so and exits.

- **Model:** `wan` (default), `seedance`, `kling`
- **Resolution:** `480p` (default), `720p`, `1080p`
- **Duration:** automatic, from the reference video (rounded to whole seconds), max 20 s.
- **Aspect ratio:** automatic, from the video.

**Kling:** Kling 3.0 has no reference-to-video, so the project uses **Kling O3 Video Edit**. It edits the input video, so the output has the same length as the input (the 20 s cap does not apply). Instead of a resolution it has a quality mode: `480p`/`720p` = `std`, `1080p` = `pro`. No audio.

## Zip inputs and outputs

Packs `media/in` and `media/out` into one zip (with `in/` and `out/` folders inside), e.g. for sharing or backup:
```powershell
.\.venv\Scripts\python.exe zip_media.py
```
The zip is saved to `zips/media_<date>.zip`. The `zips/` folder is ignored by git.

## Folders

| Folder / file | Contents |
|---|---|
| `media/in/reference-video/` | **exactly 1** video (`.mp4`, `.mov`) |
| `media/in/reference-images/` | images of the people (`.jpg`, `.png`, `.webp`), sorted alphabetically by name: the 1st file = Image 1, the 2nd = Image 2… (name them `1_….jpg`, `2_….jpg` to control the order) |
| `media/out/` | finished videos (`model_resolution_date.mp4`) |
| `prompt.py` | the prompt (`PROMPT` variable) |
| `main.py` | settings (default model, resolution, max duration, audio) and the entry point |
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
