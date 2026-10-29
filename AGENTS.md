# Agent instructions

Rules for AI coding agents (Claude Code, Codex, Copilot, …) working in this repo.

## 🚫 Never run a paid generation

Every real generation through the Higgsfield API **costs money**. Agents must never start one.

- **Never run** `python main.py` without `--test`, `higgsfield_video.py`, or any code that calls `higgsfield_client.subscribe`, `submit`, `upload_file` or the Higgsfield HTTP API.
- **Allowed:** `python main.py ... --test` (uploads and bills nothing), `python main.py --help`, `python -m pytest` (tests use fakes, no network).
- When a generation is needed, **write the exact command in the chat** and let the user run it, e.g.:
  ```bash
  python main.py genjutsu-light 480p --video football --images gazi --test   # check first
  python main.py genjutsu-light 480p --video football --images gazi          # user runs this
  ```
- Read-only API calls that cost nothing (e.g. checking the status of an existing request) are fine, but say what you are doing.

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
| `zip_media.py` | zips media, or with `--repo` what git would push |
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
