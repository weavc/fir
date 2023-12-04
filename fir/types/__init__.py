from dataclasses import dataclass
from typing import Literal

ConfigOptions = Literal[
    "status.default",
    "status.todo",
    "status.doing",
    "status.done",
    "enable.ls.hide_done_tasks",
    "enable.log_task_post_modify",
    "enable.column.due",
    "enable.column.tags",
    "enable.column.link",
    "enable.column.description",
    "enable.column.assigned",
    "enable.column.priority",
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
    "status.todo": ConfigOptionsData(
        "status.todo",
        "Comma-seperated list of todo statuses",
        "TODO,ONHOLD",
        "todo,hold"),
    "status.doing": ConfigOptionsData(
        "status.doing",
        "Comma-seperated list of doing or in progress statuses",
        "PROG,PR",
        "doing"),
    "status.done": ConfigOptionsData(
        "status.done",
        "Comma-seperated list of done statuses",
        "DONE,REJECTED",
        "done,rejected"),
    "enable.ls.hide_done_tasks": ConfigOptionsData(
        "enable.ls.hide_done_tasks",
        "1 to hide done tasks, 0 to show done tasks",
        "1",
        "1"),
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
}

StatusTypes = Literal[
    "todo",
    "doing",
    "done"]
