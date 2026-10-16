# Test documentation

Every issue that adds or changes tests gets one file here: `issue-<number>-<short-name>.md`.
Tests written before issue tracking started are documented in [`baseline.md`](baseline.md).

## Template

Copy this into `issue-<number>-<short-name>.md`:

```markdown
# Issue #<number>: <title>

**Link:** <issue URL>
**Summary:** what the issue changed and why, in 1–3 sentences.

## Tests

### `test/<file>.py::<test_name>`
- **What it checks:** expected behavior in one sentence.
- **Why:** the bug or requirement it protects.
- **Test double:** none / stub / fake / mock / spy, and what it replaces (e.g. "fake Higgsfield client instead of the real API").

<!-- repeat for every test added or changed in this issue -->

## How to run

    python -m pytest test/<file>.py -v
```

## Test doubles used in this project

| Double | What it is | Example here |
|---|---|---|
| **Stub** | returns a fixed answer, no logic | `video_duration` → `10.0` in `test_models.py` |
| **Fake** | a working but simplified implementation | `fake_higgsfield()` and `fake_mp4()` in `test/doubles.py` |
| **Mock / spy** | records calls so the test can assert on them | `fake.calls` and `downloads` in `test_generation.py` |

Shared doubles live in [`test/doubles.py`](../doubles.py). Reuse them before writing new ones.
