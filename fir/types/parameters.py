from typing import Literal

from fir.builder import CmdArg

Parameters = Literal[
    "status",
    "description",
    "task_id",
    "task_name",
    "due",
    "link",
    "priority",
    "tags",
    "assignee",
    "config_name",
    "config_value",
    "profile_set",
    "profile_path",
    "profile_name",
    "force",
]

ParameterMap: dict[Parameters, CmdArg] = {
    "status": CmdArg("status", "Set status of the task, otherwise the value provided in 'status.default' will be used.", aliases=["--status"]),
    "description": CmdArg("description", "Add a description to the task.", aliases=["--desc", "--description"]),
    "task_id": CmdArg("task_id", "Task id value. It will accept shortened values and matches on the first matching task. i.e. 'inbcjR3B' || 'inb'", aliases=["--id"]),
    "task_name": CmdArg("task_name", "Name of task, should be a short description of what needs to be done.", aliases=["-n", "--name"]),
    "due": CmdArg("due", "Set the due date of task.", aliases=["--due"]),
    "link": CmdArg("link", "Add a link to the task.", aliases=["--link"]),
    "priority": CmdArg("priority", "Set the priority of the task.", aliases=["--priority"]),
    "tags": CmdArg("tags", "Name(s) of tags against a task.", aliases=[]),
    "assignee": CmdArg("assignee", "Name(s) of people to assign to a task.", aliases=[]),
    "config_name": CmdArg("config_name", "Name of config property.", aliases=[]),
    "config_value": CmdArg("config_value", "Value to assign to config property", aliases=[]),
    "profile_set": CmdArg("profile_set", "Flag to set this profile to the current scope", aliases=["--set"]),
    "profile_path": CmdArg("profile_path", "Path to profile file or directory", aliases=[]),
    "profile_name": CmdArg("profile_name", "Profile name", aliases=[]),
    "force": CmdArg("force", "Forces operation", aliases=["--force"]),
}
