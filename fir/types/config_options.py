from dataclasses import dataclass
from typing import Literal

ConfigOptions = Literal[
    "status.default",
    "enable.log_task_post_modify",
    "enable.column.due",
    "enable.column.tags",
    "enable.column.link",
    "enable.column.description",
    "enable.column.assigned",
    "enable.column.priority",
    "name.truncate",
]


@dataclass
class ConfigOptionsData:
    name: ConfigOptions
    description: str
    example: str
    default: str


ConfigOptionsMap: dict[ConfigOptions, ConfigOptionsData] = {
    "status.default": ConfigOptionsData(
        "status.default",
        "Default status that will be used when tasks are created",
        "TODO",
        "todo"),
    "enable.column.due": ConfigOptionsData(
        "enable.column.due",
        "Show [1] or hide [0] due column",
        "1",
        "0"),
    "enable.column.tags": ConfigOptionsData(
        "enable.column.tags",
        "Show [1] or hide [0] tags column",
        "1",
        "1"),
    "enable.column.description": ConfigOptionsData(
        "enable.column.description",
        "Show [1] or hide [0] description column",
        "0",
        "0"),
    "enable.column.link": ConfigOptionsData(
        "enable.column.link",
        "Show [1] or hide [0] link column",
        "0",
        "0"),
    "enable.column.assigned": ConfigOptionsData(
        "enable.column.assigned",
        "Show [1] or hide [0] assigned column",
        "1",
        "0"),
    "enable.column.priority": ConfigOptionsData(
        "enable.column.priority",
        "Show [1] or hide [0] priority column",
        "1",
        "0"),
    "enable.log_task_post_modify": ConfigOptionsData(
        "enable.log_task_post_modify",
        "Print full task details after modifying it",
        "0",
        "0"),
    "name.truncate": ConfigOptionsData(
        "name.truncate",
        "Truncate task name in table views. 0 to disable.",
        "50",
        "50"),
}