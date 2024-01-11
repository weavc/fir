from datetime import datetime
from fir.cmd import status_commands


from fir.cmd.builder import Cmd, CmdBuilder
from fir.cmd.set_commands import SetHandlers
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
        status = self.context.profile.data.config.get("status.default", "")
        if self.context.args.get("status"):
            status = self.context.args.get("status")

        success, due = parse_date_from_arg(self.context.args.get("due"))
        if not success:
            return self.context.logger.log_error("Unable to parse date from due date")

        task_name = ' '.join(self.context.args.get("task_name"))
        task = TaskDto(generate_task_id(not_in=[t.id for t in self.context.profile.data.tasks]), task_name, due=due)

        set_status = self.context.profile.set_status(task, status)
        if not set_status:
            return self.context.logger.log_error("Invalid status provided")

        if (self.context.args.get("priority")):
            passed, priority = parse_priority_from_arg(self.context.args.get("priority"))
            if not passed:
                return self.context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")
            task.priority = priority
        if self.context.args.get("description"):
            task.description = self.context.args.get("description")
        if self.context.args.get("link"):
            task.link = self.context.args.get("link")

        self.context.profile.data.tasks.append(task)
        self.context.profile.save()

        self.context.logger.log_success(f"Added task \"{task.name}\" [{task.id}]")

        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def modify_task(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        if self.context.args.get("status") is not None:
            set_status = self.context.profile.set_status(task, self.context.args.get("status"))
            if not set_status:
                return self.context.logger.log_error("Invalid status provided")
        if self.context.args.get("task_name") is not None:
            task.name = self.context.args.get("task_name")
        if self.context.args.get("due"):
            success, due = parse_date_from_arg(self.context.args.get("due"))
            if not success:
                return self.context.logger.log_error("Unable to parse date from due date")
            task.due = due
        if (self.context.args.get("priority")):
            passed, priority = parse_priority_from_arg(self.context.args.get("priority"))
            if not passed:
                return self.context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")
            task.priority = priority
        if self.context.args.get("description"):
            task.description = self.context.args.get("description")
        if self.context.args.get("link"):
            task.link = self.context.args.get("link")

        task.modified = datetime_to_date_string(datetime.now())
        self.context.profile.save()
        self.context.logger.log_success(f"Updated task \"{task.name}\" [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def remove_task(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        self.context.profile.data.tasks.remove(task)
        self.context.profile.save()

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
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        tags = self.context.args.get("tags")

        for t in tags:
            if t not in task.tags:
                task.tags.append(t)

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def rm_tag(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        tags = self.context.args.get("tags")

        for t in tags:
            if t in task.tags:
                task.tags.remove(t)

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def add_assigned(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        assignees = self.context.args.get("assignee")

        for a in assignees:
            if a not in task.assigned_to:
                task.assigned_to.append(a)

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def rm_assigned(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        assignees = self.context.args.get("assignee")

        for a in assignees:
            if a in task.assigned_to:
                task.assigned_to.remove(a)

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def set_status(self):
        sh = SetHandlers(self.context, register=False)
        return sh.set_status()
