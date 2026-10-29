"""Settings loading (settings.load) and the tmp-prompt file (prompt.get_prompt)."""

import pytest

import prompt
import settings
from choices import PromptName


@pytest.fixture
def write(tmp_path):
    """Write a small Python config file into tmp_path. Returns its path."""
    def _write(name, text):
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return path
    return _write


# --- settings.load ---------------------------------------------------------

def test_load_uses_example_when_config_is_missing(write, tmp_path):
    example = write("config.example.py", "DEFAULT_MODEL = 'wan'\nMAX_DURATION = 20\n")

    assert settings.load(example, tmp_path / "config.py") == {
        "DEFAULT_MODEL": "wan", "MAX_DURATION": 20,
    }


def test_load_config_overrides_only_what_it_sets(write):
    example = write("config.example.py", "DEFAULT_MODEL = 'wan'\nMAX_DURATION = 20\n")
    user = write("config.py", "DEFAULT_MODEL = 'kling'\n")

    assert settings.load(example, user) == {"DEFAULT_MODEL": "kling", "MAX_DURATION": 20}


def test_load_ignores_imports_and_lowercase_names(write, tmp_path):
    example = write("config.example.py", "from pathlib import Path\nhelper = 1\nOUT_DIR = Path('out')\n")

    assert set(settings.load(example, tmp_path / "missing.py")) == {"OUT_DIR"}


def test_real_example_defines_everything_the_code_uses():
    values = settings.load(settings.ROOT / "config.example.py", settings.ROOT / "no-config.py")

    for name in ["REFERENCE_VIDEO", "REFERENCE_IMAGES", "DEFAULT_MODEL", "DEFAULT_RESOLUTION",
                 "DEFAULT_PROMPT", "GENERATE_AUDIO", "MUTE_REFERENCE_VIDEO", "MAX_DURATION",
                 "MAX_UPLOAD_MB", "MAX_SIDE_PX", "TIMEOUT_S", "TMP_PROMPT_FILE", "PRICE_MULTIPLIER",
                 "IN_VIDEO_DIR", "IN_IMAGES_DIR", "OUT_DIR", "TMP_DIR"]:
        assert name in values


def test_real_example_has_neutral_inputs():
    """The committed example must not point to someone's personal files."""
    values = settings.load(settings.ROOT / "config.example.py", settings.ROOT / "no-config.py")

    assert values["REFERENCE_VIDEO"] is None
    assert values["REFERENCE_IMAGES"] is None


def test_describe_names_config_py_when_it_exists(write):
    user = write("config.py", "X = 1\n")

    assert settings.describe(user).startswith("config.py")


def test_describe_warns_when_only_the_example_is_used(tmp_path):
    assert "no config.py" in settings.describe(tmp_path / "config.py")


# --- tmp-prompt ------------------------------------------------------------

def test_tmp_prompt_is_a_selectable_name():
    assert PromptName.TMP_PROMPT == "tmp-prompt"
    assert set(prompt.PROMPTS) <= set(PromptName)


def test_tmp_prompt_reads_the_file(tmp_path, monkeypatch):
    path = tmp_path / "tmp-prompt.txt"
    path.write_text("  Replace the person in Video 1.\n\n", encoding="utf-8")
    monkeypatch.setattr(settings, "TMP_PROMPT_FILE", path)

    assert prompt.get_prompt(PromptName.TMP_PROMPT) == "Replace the person in Video 1."


def test_tmp_prompt_missing_file_exits(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "TMP_PROMPT_FILE", tmp_path / "missing.txt")

    with pytest.raises(SystemExit, match="tmp-prompt.example.txt"):
        prompt.get_prompt("tmp-prompt")


def test_tmp_prompt_empty_file_exits(tmp_path, monkeypatch):
    path = tmp_path / "tmp-prompt.txt"
    path.write_text("   \n", encoding="utf-8")
    monkeypatch.setattr(settings, "TMP_PROMPT_FILE", path)

    with pytest.raises(SystemExit, match="is empty"):
        prompt.get_prompt("tmp-prompt")


def test_named_prompt_comes_from_prompts():
    assert prompt.get_prompt(PromptName.ONE_PERSON) == prompt.PROMPTS[PromptName.ONE_PERSON]


def test_tmp_prompt_example_file_exists():
    example = settings.ROOT / "prompts" / "tmp-prompt.example.txt"

    assert example.read_text(encoding="utf-8").strip()
