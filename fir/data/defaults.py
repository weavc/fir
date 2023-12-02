from datetime import datetime
from typing import get_args
from fir.helpers import generate_id
from fir.types import ConfigOptions, ConfigOptionsMap
from fir.types.dtos import ProfileDto, SettingsDto


def default_settings() -> SettingsDto:
    return SettingsDto("default")


def default_profile(name: str, description: str = "") -> ProfileDto:
    profile = ProfileDto(name, description, default_config())
    return profile


def default_config() -> dict[ConfigOptions, str]:
    d = {}
    for key in get_args(ConfigOptions):
        d[key] = ConfigOptionsMap.get(key).default

    return d
