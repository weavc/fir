from dataclasses import dataclass
from typing import Any, Literal

ConfigOptions = Literal[
    "status.default",
    "status.todo",
    "status.doing",
    "status.done"]


@dataclass
class ConfigOptionsData:
    name: ConfigOptions
    description: str
    example: str


ConfigOptionsMap: dict[ConfigOptions, ConfigOptionsData] = {
    "status.default": ConfigOptionsData("status.default", "Default status that will be used when tasks are created", "TODO"),
    "status.todo": ConfigOptionsData("status.todo", "Comma-seperated list of todo statuses", "TODO,ONHOLD"),
    "status.doing": ConfigOptionsData("status.doing", "Comma-seperated list of doing or in progress statuses", "PROG,PR"),
    "status.done": ConfigOptionsData("status.done", "Comma-seperated list of done statuses", "DONE,REJECTED"),
}

StatusTypes = Literal[
    "todo",
    "doing",
    "done"]
