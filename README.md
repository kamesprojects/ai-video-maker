# AI Video Maker

Replaces people in a reference video with people from photos, using the Higgsfield API.

## Setup

```bash
git clone <repo-url> && cd ai-video-maker
python -m venv .venv
source .venv/Scripts/activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                   # then put your key in: HF_KEY=key-id:key-secret
cp config.example.py config.py         # your settings (not in git)
python main.py --test                  # free check
```

API key: [console.higgsfield.ai](https://console.higgsfield.ai) → API keys.

## What it does

- **Generate** a video from a reference video + photos + prompt: `python main.py` (💰 paid).
- **Free check** with an estimated price before paying: `python main.py --test`.
- **4 models:** `wan` (default), `seedance`, `kling`, `genjutsu-light`.
- **Resolutions:** `480p`, `720p`, `1080p`.
- **Prompts:** `one-person`, `four-people`, or your own text in `prompts/tmp-prompt.txt` (`tmp-prompt`).
- **Pick inputs:** `--video NAME`, `--images A,B` (order = Image 1, Image 2).
- **Upload without sound:** `--mute`.
- **Long or big videos** are trimmed to 20 s and compressed automatically before upload.
- **Every run saves** the video + a `.json` (info, request ID, estimated cost) to `media/out/`.
- **Resize** reference videos (copies): `python resize_videos.py 480p`.
- **Cut** parts of a reference video (copies): `python trim_video.py 2-8 12-15`, or join them into one with `--combine`.
- **Zip** media, or only what git would push: `python zip_media.py [--repo]`.

All commands: [COMMANDS.md](COMMANDS.md) · all options: `python main.py --help`

## Where things are

- `media/in/reference-video/` – your videos
- `media/in/reference-images/` – your photos
- `media/out/` – results
- `config.py` – your settings (model, resolution, prompt, inputs); defaults in `config.example.py`
- `prompt.py` – prompts; `prompts/tmp-prompt.txt` – your quick prompt
- `pricing.json` – model prices for the cost estimate

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Contributing: [CONTRIBUTING.md](CONTRIBUTING.md) · AI agents: [AGENTS.md](AGENTS.md) · changes: [CHANGELOG.md](CHANGELOG.md)
