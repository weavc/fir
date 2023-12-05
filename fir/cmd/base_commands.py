from datetime import datetime


from fir.cmd.builder import Cmd, CmdBuilder
from fir.context import Context
from fir.helpers import generate_task_id
from fir.helpers.parse import parse_date_from_arg, parse_priority_from_arg
from fir.helpers.dates import datetime_to_date_string
from fir.types import StatusTypes
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

        self.register("mod", self.modify_task, description="Modify a task.", aliases=["edit"])\
            .with_positional(pm["task_id"])\
            .with_optional(pm["status"], pm["due"], pm["link"], pm["priority"], pm["description"], pm["task_name"])

        self.register("rm", self.remove_task, description="Remove a task.")\
            .with_positional(pm["task_id"])

        self.register("info", self.task_info, description="Prints all information for given task.", aliases=["i"])\
            .with_positional(pm["task_id"])

        self.register("ls", self.ls, description="List tasks", aliases=["list"])\
            .with_optional(pm["status"], pm["task_name"], pm["assignee"], pm["tags"])

        self.register("description", self.set_description, aliases=["desc"],
                      description="Add a description to a task.")\
            .with_positional(pm["task_id"], pm["description"].with_overrides(nargs="+"))

        self.register(
            "link",
            self.set_link,
            aliases=["ln"],
            description="Add a link to a task. i.e. https://github.com/weavc/fir/issues/1")\
            .with_positional(pm["task_id"], pm["link"])

        self.register("priority", self.set_priority, description="Set priority level of a task (1-999). Default: 100.")\
            .with_positional(pm["task_id"], pm["priority"])

        self.register("tag", self.add_tag, description="Add tag(s) to a task.")\
            .with_positional(pm["task_id"], pm["tags"].with_overrides(nargs="+"))

        self.register("rmtag", self.rm_tag, description="Remove tag(s) from a task.", aliases=["rmt"])\
            .with_positional(pm["task_id"], pm["tags"].with_overrides(nargs="+"))

        self.register("assign", self.add_assigned, description="Add person(s) to a task.")\
            .with_positional(pm["task_id"], pm["tags"].with_overrides(nargs="+"))

        self.register("unassign", self.rm_assigned, description="Remove person(s) from a task.")\
            .with_positional(pm["task_id"], pm["tags"].with_overrides(nargs="+"))

        self.register("", self.ls_category, description="List all tasks with the matching status", aliases=[])\
            .with_optional(pm["task_name"], pm["assignee"], pm["tags"])

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
            self.context.log_task(task)

    def modify_task(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

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
            self.context.log_task(task)

    def remove_task(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        self.context.profile.data.tasks.remove(task)
        self.context.profile.save()

        return self.context.logger.log_success(f"Removed task {task.name} [{task.id}]")

    def task_info(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        self.context.log_task(task)

    def ls(self, category: str = None):
        tasks = []
        for task in self.context.profile.data.tasks:
            if self.context.args.get("status") and task.status != self.context.args.get("status"):
                continue
            if self.context.args.get("task_name") and not self.context.args.get(
                    "task_name").lower() in task.name.lower():
                continue
            if self.context.args.get("assignee") and self.context.args.get("assignee") not in task.assigned_to:
                continue
            if self.context.args.get("tags") and self.context.args.get("tags") not in task.tags:
                continue

            status = self.context.profile.get_status_by_name(task.status)
            if status and not category and status.hide_by_default:
                continue

            if category and category != task.status:
                continue

            tasks.append(task)

        self.context.log_task_table(tasks)

    def ls_category(self):
        return self.ls(self.context.args.get("status"))

    def set_description(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        task.description = ' '.join(self.context.args.get("description"))

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.log_task(task)

    def set_link(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        task.link = self.context.args.get("link")

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.log_task(task)

    def set_priority(self, context: Context):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        passed, priority = parse_priority_from_arg(self.context.args.get("priority"))
        if not passed:
            return self.context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")

        task.priority = priority

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.log_task(task)

    def add_tag(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        tags = self.context.args.get("tags")

        for t in tags:
            if t not in task.tags:
                task.tags.append(t)

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.log_task(task)

    def rm_tag(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        tags = self.context.args.get("tags")

        for t in tags:
            if t in task.tags:
                task.tags.remove(t)

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.log_task(task)

    def add_assigned(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        assignees = self.context.args.get("assignee")

        for a in assignees:
            if a not in task.assigned_to:
                task.assigned_to.append(a)

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.log_task(task)

    def rm_assigned(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        assignees = self.context.args.get("assignee")

        for a in assignees:
            if a in task.assigned_to:
                task.assigned_to.remove(a)

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.log_task(task)
