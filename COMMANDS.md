# Commands

Shows all options and examples.
```bash
python main.py --help
```
Returns: the help text.

Checks everything for free, uploads and bills nothing.
```bash
python main.py --test
```
Returns: model, prompt, video, images, parameters and the estimated cost.

Runs a paid generation with the settings from `config.py`.
```bash
python main.py
```
Returns: the video and a `.json` with info and cost in `media/out/`.

Runs with a different model, resolution or prompt than in `config.py` (add `--test` to check first).
```bash
python main.py genjutsu-light 480p tmp-prompt
```
Returns: the video and the `.json` in `media/out/`.

Uses a specific video and images in this order.
```bash
python main.py --video boxing --images person1,person2
```
Returns: the video and the `.json` in `media/out/`.

Uploads the reference video without sound.
```bash
python main.py --mute
```
Returns: the video and the `.json` in `media/out/` (`_muted` in the name).

Makes smaller copies of the reference videos (resolution from `RESIZE_TO` in `config.py`), originals are kept.
```bash
python resize_videos.py
```
Returns: `<name>_480p.mp4` next to each video in `media/in/reference-video/`; videos already that small are skipped.

Makes smaller copies of all reference videos in the resolution you choose.
```bash
python resize_videos.py 720p
```
Returns: `<name>_720p.mp4` next to each video; videos already that small are skipped.

Makes a smaller copy of one video in the resolution you choose.
```bash
python resize_videos.py 720p --video boxing
```
Returns: `boxing-video_720p.mp4`; use it with `python main.py --video boxing-video_720p`.

Cuts a part of the reference video into a new copy (seconds from-to), the original is kept.
```bash
python trim_video.py 2-8
```
Returns: `boxing-video_2-8s.mp4` next to the video; the video comes from `REFERENCE_VIDEO` in `config.py`.

Cuts several parts of a chosen video at once (decimals and minutes:seconds work too).
```bash
python trim_video.py 2-8 12-15 1:05-1:20 --video boxing
```
Returns: one copy per part, e.g. `boxing-video_2-8s.mp4`, `boxing-video_12-15s.mp4`, `boxing-video_1m05-1m20s.mp4`.

Cuts several parts and joins them in order into one video.
```bash
python trim_video.py 4-11 22-26 --video song --combine
```
Returns: one copy, e.g. `song_4-11+22-26s.mp4` (7 s + 4 s = 11 s).

Zips `media/in` and `media/out`.
```bash
python zip_media.py
```
Returns: `zips/media_<date>.zip`.

Zips only what git would push.
```bash
python zip_media.py --repo
```
Returns: `zips/repo_<date>.zip`.

Runs all tests, free and offline.
```bash
python -m pytest
```
Returns: `N passed`, or the failing tests.
