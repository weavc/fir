from typing import get_args
from fir.types.config_options import ConfigOptions, ConfigOptionsMap
from fir.types.dtos import ProfileDto, SettingsDto, StatusDto


def default_settings() -> SettingsDto:
    return SettingsDto("default")


def default_statuses() -> list[StatusDto]:
    return [
        StatusDto("todo", "light_red", 750),
        StatusDto("hold", "light_yellow", 800),
        StatusDto("prog", "light_blue", 600),
        StatusDto("done", "light_green", 500, hide_by_default=True),
        StatusDto("rejected", "red", 850, hide_by_default=True),
        StatusDto("backlog", "light_cyan", 900, hide_by_default=True),
    ]


def default_profile(name: str, description: str = "") -> ProfileDto:
    profile = ProfileDto(name, description, default_config(), statuses=default_statuses())
    return profile


def default_config() -> dict[ConfigOptions, str]:
    d = {}
    for key in get_args(ConfigOptions):
        d[key] = ConfigOptionsMap.get(key).default

    return d
