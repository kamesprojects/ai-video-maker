"""Command-line arguments and prompt selection (main.parse_args, prompt.PROMPTS)."""

from pathlib import Path

import pytest

import main
import settings
from choices import PromptName, Resolution
from prompt import PROMPTS
from settings import DEFAULT_PROMPT


def test_defaults_without_arguments():
    assert main.parse_args([]) == (
        settings.DEFAULT_MODEL, settings.DEFAULT_RESOLUTION, settings.DEFAULT_PROMPT, False,
        settings.MUTE_REFERENCE_VIDEO, settings.REFERENCE_VIDEO,
        main.name_list(settings.REFERENCE_IMAGES),
    )


def test_config_inputs_are_used_without_arguments(monkeypatch):
    monkeypatch.setattr(settings, "REFERENCE_VIDEO", "football")
    monkeypatch.setattr(settings, "REFERENCE_IMAGES", ["anna", "ben"])
    monkeypatch.setattr(settings, "MUTE_REFERENCE_VIDEO", True)

    args = main.parse_args([])

    assert (args.video, args.images, args.mute) == ("football", ["anna", "ben"], True)


def test_command_line_overrides_config(monkeypatch):
    monkeypatch.setattr(settings, "REFERENCE_VIDEO", "football")
    monkeypatch.setattr(settings, "REFERENCE_IMAGES", ["anna"])

    args = main.parse_args(["--video", "song", "--images", "ben"])

    assert (args.video, args.images) == ("song", ["ben"])


def test_arguments_in_any_order_and_case():
    result = main.parse_args(["FOUR-PEOPLE", "--test", "720p", "seedance"])

    assert result[:4] == ("seedance", "720p", "four-people", True)


@pytest.mark.parametrize("prompt_name", list(PromptName))
def test_every_prompt_can_be_selected(prompt_name):
    assert main.parse_args([prompt_name])[2] == prompt_name


def test_unknown_argument_lists_the_options():
    with pytest.raises(SystemExit, match=f"prompts: {', '.join(PromptName)}"):
        main.parse_args(["two-people"])


@pytest.mark.parametrize("flag", ["--help", "-h", "--HELP"])
def test_help_prints_usage_and_exits_ok(flag, capsys):
    with pytest.raises(SystemExit) as exit_info:
        main.parse_args(["seedance", flag, "--test"])

    output = capsys.readouterr().out
    assert exit_info.value.code == 0
    assert "Usage: python main.py" in output


def test_help_lists_every_option():
    text = main.help_text()

    for name in [*main.MODELS, *Resolution, *PromptName, *main.FLAGS, "--help"]:
        assert name in text
    assert f"{main.DEFAULT_MODEL} (default)" in text
    assert f"{DEFAULT_PROMPT} (default)" in text


def test_mute_flag():
    args = main.parse_args(["--MUTE", "kling"])

    assert args.mute is True
    assert args.model == "kling"
    assert main.parse_args([]).mute is False


@pytest.mark.parametrize("has_audio, mute, expected", [
    (True, False, "sent with the video"),
    (True, True, "removed before upload (--mute)"),
    (False, True, "none in the video"),
])
def test_audio_summary(monkeypatch, has_audio, mute, expected):
    monkeypatch.setattr(main, "has_audio", lambda _: has_audio)

    assert main.audio_summary(Path("v.mp4"), mute) == expected


def test_default_prompt_exists():
    """Any PromptName is valid, including TMP_PROMPT (its text comes from a file)."""
    assert DEFAULT_PROMPT in list(PromptName)


def test_option_names_do_not_overlap():
    """A name in two lists would make the argument ambiguous."""
    names = [*main.MODELS, *Resolution, *PromptName]

    assert len(names) == len(set(names))


@pytest.mark.parametrize("prompt_name", list(PROMPTS))
def test_prompts_reference_the_inputs(prompt_name):
    """Every prompt must tell the model which input is the video and which are images."""
    text = PROMPTS[prompt_name]

    assert "Video 1" in text
    assert "reference image" in text


def test_every_prompt_name_has_a_text():
    """Every PromptName has a text in PROMPTS, except TMP_PROMPT (read from a file)."""
    assert set(PROMPTS) | {PromptName.TMP_PROMPT} == set(PromptName)
    assert PromptName.TMP_PROMPT not in PROMPTS


def test_prompt_is_returned_as_prompt_name():
    assert main.parse_args(["four-people"]).prompt is PromptName.FOUR_PEOPLE


def test_unknown_default_prompt_exits(monkeypatch):
    monkeypatch.setattr(main, "DEFAULT_PROMPT", "boxing")

    with pytest.raises(SystemExit, match="Unknown PromptName 'boxing'.*DEFAULT_PROMPT"):
        main.parse_args([])


def test_resolution_is_returned_as_resolution_key():
    assert main.parse_args(["1080P"]).resolution is Resolution.P1080


def test_unknown_default_resolution_exits(monkeypatch):
    monkeypatch.setattr(main, "DEFAULT_RESOLUTION", "4k")

    with pytest.raises(SystemExit, match="Unknown Resolution '4k'.*DEFAULT_RESOLUTION"):
        main.parse_args([])
