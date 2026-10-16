# Vision

## Why this exists

Swapping people into an existing video with AI is possible today, but in practice it means clicking through web UIs, re-uploading the same files, guessing parameters per model and paying for mistakes. This project turns that into one repeatable command: put a reference video and photos in a folder, pick a model and get the result.

## What we are building

A small, local, open tool that:

- **takes a reference video + reference images + a prompt** and produces a new video with the people replaced, keeping the original motion, framing and timing;
- **is model-agnostic**: Wan, Seedance and Kling today, and adding a model means adding one class in `models/`;
- **protects the user's money**: nothing is billed without an explicit command, `--test` always shows exactly what would be sent, and inputs (duration, aspect ratio) are derived from the video so a run isn't wasted on wrong settings;
- **protects the user's data**: photos, videos and API keys stay on the user's machine and never end up in git;
- **remembers everything**: every input, generation and output is recorded (SurrealDB as the source of truth, see issue #1), so results can be traced, compared and reproduced.

## Principles

1. **Explicit over automatic for anything that costs money.** A paid action is always a deliberate user command.
2. **Fail loudly, never fake success.** Failed, cancelled or moderated generations are reported as such.
3. **Simple to run.** A fresh clone gets to a working `--test` by following the README, with no extra services beyond what is documented.
4. **Small, readable code.** Every contributor should be able to understand the whole flow: `main.py` → `models/` → `generation/`.
5. **Tested without the network.** The test suite uses test doubles and never calls the real API.

## Roadmap

- **Now:** CLI for Wan 3.0, Seedance 2.5 and Kling O3, automatic duration and aspect ratio, zip export.
- **Next (#1):** SurrealDB as the source of truth: encrypted API key, records of inputs, generations and outputs.
- **Later (ideas, not commitments):**
  - a generation history (list, re-run, compare models on the same input)
  - cost estimate before a run
  - batch runs (one input, several models or prompts)
  - a simple local UI

## Non-goals

- Hosting a public service or handling other people's payments.
- Training or fine-tuning models.
- Deepfakes of people without their consent. The tool is for people who agreed to appear in the video.
