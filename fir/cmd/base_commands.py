from datetime import datetime
from fir.cmd import status_commands
from fir.cmd.builder import Cmd, CmdBuilder
from fir.cmd.set_commands import SetHandlers
from fir.handlers import set, base
from fir.context import Context
from fir.utils import generate_task_id
from fir.utils.parse import parse_date_from_arg, parse_priority_from_arg
from fir.utils.dates import datetime_to_date_string
from fir.types.dtos import TaskDto
from fir.types.parameters import ParameterMap as pm


class CommandHandlers(CmdBuilder):
    name = None
    aliases = []
    cmds: dict[str, Cmd] = {}
    context: Context

    def __init__(self, context: Context):
        self.context = context

        self.register("new", self.create_task, description="Add a new task.", aliases=["add"])\
            .with_positional(pm["task_name"].with_overrides(nargs="+"))\
            .with_optional(pm["status"], pm["due"], pm["link"], pm["priority"], pm["description"])

        self.register("modify", self.modify_task, description="Modify a task.", aliases=["edit", "mod"])\
            .with_positional(pm["task_id"])\
            .with_optional(pm["status"], pm["due"], pm["link"], pm["priority"], pm["description"], pm["task_name"])
        
        self.register("mods", SetHandlers(context, register=False).set_status, description="Update the status of a task.", aliases=["ms"])\
            .with_positional(pm["task_id"], pm["status"])
        
        self.register("remove", self.remove_task, description="Remove a task.", aliases=["rm"])\
            .with_positional(pm["task_id"])

        self.register("info", self.task_info, description="Prints all information for given task.", aliases=["i"])\
            .with_positional(pm["task_id"])

        self.register("list", self.ls, description="List tasks", aliases=["ls"])\
            .with_optional(pm["status"], pm["task_name"], pm["assignee"], pm["tags"])\
            .with_flag(pm["all"])

        self.register("tag", self.add_tag, description="Add tag(s) to a task.")\
            .with_positional(pm["task_id"], pm["tags"].with_overrides(nargs="+"))

        self.register("rmtag", self.rm_tag, description="Remove tag(s) from a task.", aliases=["rmt"])\
            .with_positional(pm["task_id"], pm["tags"].with_overrides(nargs="+"))

        self.register("assign", self.add_assigned, description="Add person(s) to a task.")\
            .with_positional(pm["task_id"], pm["assignee"].with_overrides(nargs="+"))

        self.register("unassign", self.rm_assigned, description="Remove person(s) from a task.")\
            .with_positional(pm["task_id"], pm["assignee"].with_overrides(nargs="+"))
        
        self.register("set-status", self.set_status, description="Set the status of a task.", aliases=["ss"])\
            .with_positional(pm["task_id"], pm["status"])

    def create_task(self):
        task, err = base.add_assigned(self.context)
        if err is not None:
            return self.context.logger.log_error(err)

        self.context.logger.log_success(f"Added task \"{task.name}\" [{task.id}]")

        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def modify_task(self):
        task, err = base.modify_task(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        self.context.logger.log_success(f"Updated task \"{task.name}\" [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def remove_task(self):
        task, err = base.add_assigned(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        return self.context.logger.log_success(f"Removed task {task.name} [{task.id}]")

    def task_info(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        self.context.logging.profile.log_task(task)

    def ls(self):
        tasks = []
        for task in self.context.profile.data.tasks:
            if self.context.args.get("status") and task.status != self.context.args.get("status"):
                continue
            if self.context.args.get("task_name") and not \
                    self.context.args.get("task_name").lower() in task.name.lower():
                continue
            if self.context.args.get("assignee") and self.context.args.get("assignee") not in task.assigned_to:
                continue
            if self.context.args.get("tags") and self.context.args.get("tags") not in task.tags:
                continue

            get_all = self.context.args.get("all", False)
            status = self.context.profile.get_status_by_name(task.status)
            if not get_all and task.status != self.context.args.get("status") and status.hide_by_default:
                continue

            tasks.append(task)

        self.context.logging.profile.log_task_table(tasks)

    def ls_category(self):
        return self.ls(self.context.args.get("status"))

    def add_tag(self):
        task, err = base.add_tag(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def rm_tag(self):
        task, err = base.rm_tag(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def add_assigned(self):
        task, err = base.add_assigned(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
         
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def rm_assigned(self):
        task, err = base.rm_assigned(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def set_status(self):
        set.status(self.context)