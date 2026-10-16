"""Command-line arguments and prompt selection (main.parse_args, prompt.PROMPTS)."""

from pathlib import Path

import pytest

import main
from prompt import DEFAULT_PROMPT, PROMPTS


def test_defaults_without_arguments():
    assert main.parse_args([]) == ("wan", "480p", DEFAULT_PROMPT, False, False)


def test_arguments_in_any_order_and_case():
    result = main.parse_args(["FOUR-PEOPLE", "--test", "720p", "seedance"])

    assert result == ("seedance", "720p", "four-people", True, False)


@pytest.mark.parametrize("prompt_name", list(PROMPTS))
def test_every_prompt_can_be_selected(prompt_name):
    assert main.parse_args([prompt_name])[2] == prompt_name


def test_unknown_argument_lists_the_options():
    with pytest.raises(SystemExit, match="prompts: one-person, four-people"):
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

    for name in [*main.MODELS, *main.RESOLUTIONS, *PROMPTS, *main.FLAGS, "--help"]:
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
    assert DEFAULT_PROMPT in PROMPTS


def test_option_names_do_not_overlap():
    """A name in two lists would make the argument ambiguous."""
    names = [*main.MODELS, *main.RESOLUTIONS, *PROMPTS]

    assert len(names) == len(set(names))


@pytest.mark.parametrize("prompt_name", list(PROMPTS))
def test_prompts_reference_the_inputs(prompt_name):
    """Every prompt must tell the model which input is the video and which are images."""
    text = PROMPTS[prompt_name]

    assert "Video 1" in text
    assert "reference image" in text
