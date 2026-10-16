# Contributing

Thanks for helping. Start with [`README.md`](README.md) (setup) and [`VISION.md`](VISION.md) (where the project is going).

## Workflow

1. Pick an issue (or open one first for anything non-trivial).
2. Create a branch: `issue-<number>-<short-name>`, e.g. `issue-1-surrealdb`.
3. Make the change, **with tests** (see below).
4. Update the docs (see [Definition of done](#definition-of-done)).
5. Open a pull request that references the issue (`Closes #<number>`).

## Using AI

You **may** use AI tools (Claude, Copilot, ChatGPT…) to write code, tests and docs. But:

- **You are the author.** You must understand every line you submit and be able to explain it in review. "The AI wrote it" is not an answer.
- **Check the facts.** AI tools invent API fields, endpoints and library functions. Verify against the official docs (e.g. the Higgsfield model API reference) before relying on them.
- **Never give AI tools your secrets.** Don't paste API keys, `.env` contents or private photos/videos into an AI chat.
- **No paid runs on autopilot.** An AI agent must not run a real generation. Paid runs are started by a human, on purpose.

## Tests

Every change is tested in the [`test/`](test/) folder. **No exceptions** for "small" changes.

- Tests use **test doubles** instead of real external things: stubs, fakes, mocks, spies, whatever the case needs. See the table in [`test/docs/README.md`](test/docs/README.md).
- Tests **never** call the real Higgsfield API, never need a real API key and never bill credits. Use `fake_higgsfield()` from [`test/doubles.py`](test/doubles.py).
- Tests don't depend on files in `media/` or on your `.env`. Create what you need in `tmp_path`.
- Put reusable doubles in `test/doubles.py` instead of copying them between tests.
- A bug fix comes with a test that fails without the fix.

Run the suite:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt   # once
.\.venv\Scripts\python.exe -m pytest -v
```

## Definition of done

A pull request is ready to merge when **all** of these are true:

- [ ] All tests pass (`python -m pytest`).
- [ ] New or changed behavior has tests in `test/`.
- [ ] **Test docs:** `test/docs/issue-<number>-<short-name>.md` describes the issue and **every** test added or changed (template in [`test/docs/README.md`](test/docs/README.md)).
- [ ] **Changelog:** [`CHANGELOG.md`](CHANGELOG.md) has an entry under `Unreleased` listing what was added, changed or fixed, with the issue number.
- [ ] **Docs:** `README.md` (and `VISION.md` if direction changed) are updated if setup, commands, folders or behavior changed.
- [ ] `python main.py --test` still works.
- [ ] No secrets, `.env`, media files or generated videos in the diff (check `git status` before committing).

## Code style

- Match the surrounding code: English names, short functions, type hints on public functions.
- Model-specific logic belongs in its class in `models/`, shared helpers in `utils.py`, API calls in `generation/`.
- Never print or log API keys or other secrets.
- New settings go into `config.example.py` (with a comment), never only into your own `config.py`. Code reads them via `settings`.
