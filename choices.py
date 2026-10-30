"""Everything you can choose: models, resolutions, prompts. Use them in config.py, e.g.
    DEFAULT_MODEL = ModelName.WAN
    DEFAULT_RESOLUTION = Resolution.P480
    DEFAULT_PROMPT = PromptName.ONE_PERSON

No project imports here, so config files can import this module.
"""

from enum import Enum


class Key(str, Enum):
    """A key equals its text ("wan") and prints as it, so plain text works too."""

    def __str__(self) -> str:
        return self.value


class ModelName(Key):
    """The value is what you type on the command line: python main.py <value>."""

    WAN = "wan"
    SEEDANCE = "seedance"
    KLING = "kling"
    GENJUTSU_LIGHT = "genjutsu-light"


class Resolution(Key):
    """Output resolution. Kling has a quality mode instead: 480p/720p = std, 1080p = pro."""

    P480 = "480p"
    P720 = "720p"
    P1080 = "1080p"


class PromptName(Key):
    """The value is what you type on the command line. Texts are in prompt.py."""

    ONE_PERSON = "one-person"
    ONE_PERSON_ONLY_FACE = "one-person-only-face"
    FOUR_PEOPLE = "four-people"
    TMP_PROMPT = "tmp-prompt"   # text from prompts/tmp-prompt.txt
