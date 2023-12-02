from dataclasses import dataclass
from typing import Any, Literal

ConfigOptions = Literal[
    "status.default",
    "status.todo",
    "status.doing",
    "status.done",
    "enable.ls.hide_done_tasks",
    "enable.ls.column.due",
    "enable.ls.column.tags"]


@dataclass
class ConfigOptionsData:
    name: ConfigOptions
    description: str
    example: str
    default: str


ConfigOptionsMap: dict[ConfigOptions, ConfigOptionsData] = {
    "status.default": ConfigOptionsData("status.default", "Default status that will be used when tasks are created", "TODO", "todo"),
    "status.todo": ConfigOptionsData("status.todo", "Comma-seperated list of todo statuses", "TODO,ONHOLD", "todo,hold"),
    "status.doing": ConfigOptionsData("status.doing", "Comma-seperated list of doing or in progress statuses", "PROG,PR", "doing"),
    "status.done": ConfigOptionsData("status.done", "Comma-seperated list of done statuses", "DONE,REJECTED", "done,rejected"),
    "enable.ls.hide_done_tasks": ConfigOptionsData("enable.ls.hide_done_tasks", "1 to hide done tasks, 0 to show done tasks", "1", "1"),
    "enable.ls.column.due": ConfigOptionsData("enable.ls.column.due", "Show [1] or hide [0] due column", "1", "0"),
    "enable.ls.column.tags": ConfigOptionsData("enable.ls.column.tags", "Show [1] or hide [0] tags column", "1", "1"),
}

StatusTypes = Literal[
    "todo",
    "doing",
    "done"]
