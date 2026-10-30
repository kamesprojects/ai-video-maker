# Agent instructions

Rules for AI coding agents (Claude Code, Codex, Copilot, …) working in this repo.

## 🚫 Never run a paid generation

Every real generation through the Higgsfield API **costs money**. Agents must never start one.

- **Never run** `python main.py` without `--test`, `higgsfield_video.py`, or any code that calls `higgsfield_client.subscribe`, `submit`, `upload_file` or the Higgsfield HTTP API.
- **Allowed:** `python main.py ... --test` (uploads and bills nothing), `python main.py --help`, `python -m pytest` (tests use fakes, no network).
- When a generation is needed, **write the exact command in the chat** and let the user run it, e.g.:
  ```bash
  python main.py genjutsu-light 480p --video dance --images anna --test   # check first
  python main.py genjutsu-light 480p --video dance --images anna          # user runs this
  ```
- Read-only API calls that cost nothing (e.g. checking the status of an existing request) are fine, but say what you are doing.

## 🔒 Privacy: nothing personal on GitHub

This repo is public. Nothing from the user's machine or life may end up in a file git pushes:

- **No absolute or local paths**: no `C:\...`, `C:/Users/...`, home folders, school or other project folders. Use relative paths (`media/in/...`) or neutral examples (`D:/other-project/...`).
- **No personal data**: no real names of people from the user's photos/videos, e-mails or account details. Use neutral names in examples and tests (`anna`, `ben`, `person1`).
- **Local-only tools stay local**: they go into `.git/info/exclude` (never into `.gitignore`, which is pushed) and are not mentioned in any committed file.
- **Before finishing a change**, check what git would push: `git ls-files --cached --others --exclude-standard`, and grep those files for paths and names.

## Secrets and personal files

- Never read, print, log or commit `.env` (API key). Ask the user to edit it themselves.
- `config.py`, `prompts/tmp-prompt.txt` and everything in `media/` are personal and ignored by git. Don't commit them; change `config.py` only when the user asks.
- Never commit or push unless the user asks.

## Project map

| Path | What it is |
|---|---|
| `main.py` | entry point: arguments, summary, `--test`, run |
| `config.example.py` | default settings (committed); new settings go here |
| `config.py` | the user's own settings (not in git) |
| `settings.py` | merges both; code reads settings from here |
| `choices.py` | `ModelName`, `Resolution`, `PromptName` keys, used in config (`DEFAULT_MODEL = ModelName.WAN`) |
| `models/` | one class per model: endpoint and API parameters |
| `generation/generate.py` | upload, request, status check, download |
| `generation/record.py` | cost estimate + the JSON record saved next to every output |
| `pricing.json`, `pricing.py` | list prices per model (from the Higgsfield docs) and the estimate |
| `prompt.py` | `PROMPTS` + `tmp-prompt` (text from `prompts/tmp-prompt.txt`) |
| `utils.py` | files, video info, ffmpeg trim/compress/mute, API key loading |
| `resize_videos.py` | downscaled copies of reference videos (`RESIZE_TO` or a CLI resolution) |
| `trim_video.py` | cuts parts (START-END seconds) of a reference video into copies |
| `zip_media.py` | zips media, or with `--repo` what git would push |
| `COMMANDS.md` | all commands and what they return; update it when commands change |
| `docs/api/` | copies of Higgsfield API docs for the models we use |
| `test/` | pytest suite; `test/docs/` documents every test |

## Working rules

Follow [`CONTRIBUTING.md`](CONTRIBUTING.md). In short, for every change:

1. Add or update tests in `test/` using test doubles (stubs, fakes, spies). No network, no real API.
2. Document every new or changed test in `test/docs/`.
3. Add an entry to `CHANGELOG.md`.
4. Update `README.md` if commands, settings, folders or behavior change.
5. Run `python -m pytest` and `python main.py --test` before saying it works.

Before adding or changing a model, read its API reference (Higgsfield publishes LLM-readable docs, see `docs/api/` and https://docs.higgsfield.ai/llms-full.txt). Don't guess parameter names: some APIs reject unknown fields.

Code style: English names, short functions with one job, match the surrounding code.
