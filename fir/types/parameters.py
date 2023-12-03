from dataclasses import dataclass, field
from typing import Literal


Parameters = Literal[
    "status",
    "description",
    "task_id",
    "task_name",
    "due",
    "link",
    "priority",
    "tags",
    "assignee"
]

@dataclass
class ParameterData:
    name: Parameters
    description: str
    flags: list[str] = field(default_factory=list[str])
    nargs: str = None


ParameterMap: dict[Parameters, ParameterData] = {
    "status": ParameterData("status", "Set status of the task, otherwise the value provided in 'status.default' will be used.", ["--status"]),
    "description": ParameterData("description", "Add a description to the task.", ["--desc", "--description"]),
    "task_id": ParameterData("task_id", "Task id value. It will accept shortened values and matches on the first matching task. i.e. 'inbcjR3B' || 'inb'", ["--id"]),
    "task_name": ParameterData("task_name", "Name of task, should be a short description of what needs to be done.", ["-n", "--name"]),
    "due": ParameterData("due", "Set the due date of task.", ["--due"]),
    "link": ParameterData("link", "Add a link to the task.", ["--link"]),
    "priority": ParameterData("priority", "Set the priority of the task.", ["--priority"]),
    "tags": ParameterData("tags", "Name(s) of tags against a task.", []),
    "assignee": ParameterData("assignee", "Name(s) of people to assign to a task.", []),
}
