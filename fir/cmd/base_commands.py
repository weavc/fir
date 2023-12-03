from datetime import datetime


from fir.builder import Cmd, CmdBuilder
from fir.context import Context
from fir.helpers import generate_task_id
from fir.helpers.parse import parse_date_from_arg, parse_priority_from_arg
from fir.helpers.dates import datetime_to_date_string
from fir.types.dtos import TaskDto
from fir.types.parameters import ParameterMap as pm


class CommandHandlers(CmdBuilder):
    name = None
    aliases = []
    cmds: dict[str, Cmd] = {}

    def __init__(self):
        self.register_commands(*[t for t in self.map()])

    def map(self) -> list[Cmd]:
        return [
            Cmd("new",
                "Add a new task.",
                aliases=["add"],
                args=[pm["task_name"].with_overrides(nargs="+")],
                optionals=[pm["status"], pm["due"], pm["link"], pm["priority"], pm["description"]],
                func=self.create_task),
            Cmd("mod",
                "Modify a task.",
                aliases=["edit"],
                args=[pm["task_id"]],
                optionals=[pm["status"], pm["due"], pm["link"], pm["priority"], pm["description"], pm["task_name"]],
                func=self.modify_task),
            Cmd("rm",
                description="Remove a task.",
                args=[pm["task_id"]],
                func=self.remove_task),
            Cmd("info",
                aliases=["i"],
                description="Prints all information for given task.",
                args=[pm["task_id"]],
                func=self.task_info),
            Cmd("list",
                aliases=["ls"],
                description="List all tasks.",
                optionals=[pm["task_id"], pm["status"], pm["task_name"]],
                func=self.ls),
            Cmd("status",
                description="Set the status of a task.",
                args=[pm["task_id"], pm["status"]],
                func=self.set_status),
            Cmd("description",
                aliases=["desc"],
                description="Add a description to a task.",
                args=[pm["task_id"], pm["description"].with_overrides(nargs="+")],
                func=self.set_description),
            Cmd("link",
                aliases=["ln"],
                description="Add a link to a task. i.e. https://github.com/weavc/fir/issues/1",
                args=[pm["task_id"], pm["link"]],
                func=self.set_link),
            Cmd("priority",
                description="Set priority level of a task (1-999). Default: 100.",
                args=[pm["task_id"], pm["priority"]],
                func=self.set_priority),
            Cmd("tag",
                description="Add tag(s) to task.",
                args=[pm["task_id"], pm["tags"].with_overrides(nargs="+")],
                func=self.add_tag),
            Cmd("rmtag",
                aliases=["rmt"],
                description="Remove tag(s) from task.",
                args=[pm["task_id"], pm["tags"].with_overrides(nargs="+")],
                func=self.rm_tag),
            Cmd("assign",
                description="Assign person(s) to task.",
                args=[pm["task_id"], pm["assignee"].with_overrides(nargs="+")],
                func=self.add_assigned),
            Cmd("unassign",
                description="Remove person(s) from task.",
                args=[pm["task_id"], pm["assignee"].with_overrides(nargs="+")],
                func=self.rm_assigned),
            Cmd("todo", description="List all todo tasks.", func=self.ls_todo),
            Cmd("doing", aliases=["prog"], description="List all in progress tasks.", func=self.ls_doing),
            Cmd("done", description="List all done/completed tasks.", func=self.ls_done),
        ]

    def create_task(self, context: Context):
        status = context.profile.data.config.get("status.default", "")
        if context.args.get("status"):
            status = context.args.get("status")

        success, due = parse_date_from_arg(context.args.get("due"))
        if not success:
            return context.logger.log_error(f"Unable to parse date from due date")

        task_name = ' '.join(context.args.get("task_name"))
        task = TaskDto(generate_task_id(not_in=context.profile.data.tasks), task_name, due=due)

        set_status = context.profile.set_status(task, status)
        if not set_status:
            return context.logger.log_error("Invalid status provided")

        if (context.args.get("priority")):
            passed, priority = parse_priority_from_arg(context.args.get("priority"))
            if not passed:
                return context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")
            task.priority = priority
        if context.args.get("description"):
            task.description = context.args.get("description")
        if context.args.get("link"):
            task.link = context.args.get("link")

        context.profile.data.tasks.append(task)
        context.profile.save()

        context.logger.log_success(f"Added task {task.name} [{task.id}]")

        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(context, task)

    def modify_task(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        if context.args.get("status") is not None:
            set_status = context.profile.set_status(task, context.args.get("status"))
            if not set_status:
                return context.logger.log_error("Invalid status provided")
        if context.args.get("name") is not None:
            task.name = context.args.get("name")
        if context.args.get("due"):
            success, due = parse_date_from_arg(context.args.get("due"))
            if not success:
                return context.logger.log_error(f"Unable to parse date from due date")

            task.due = due
        if (context.args.get("priority")):
            passed, priority = parse_priority_from_arg(context.args.get("priority"))
            if not passed:
                return context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")
            task.priority = priority
        if context.args.get("description"):
            task.description = context.args.get("description")
        if context.args.get("link"):
            task.link = context.args.get("link")

        task.modified = datetime_to_date_string(datetime.now())
        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)

    def remove_task(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        context.profile.data.tasks.remove(task)
        context.profile.save()

        return context.logger.log_success(f"Removed task {task.name} [{task.id}]")

    def task_info(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        context.log_task(task)

    def ls(self, context: Context):
        tasks = []
        for task in context.profile.data.tasks:
            if context.args.get("status") is not None and task.status != context.args.get("status"):
                continue
            if context.args.get("id") is not None and not task.id.startswith(context.args.get("id")):
                continue
            if context.args.get("name") is not None and not context.args.get("name").lower() in task.name.lower():
                continue

            if context.profile.try_get_config_value_bool("enable.ls.hide_done_tasks"):
                if context.profile.check_status_type(task.status) == "done":
                    continue

            tasks.append(task)

        context.log_task_table(tasks)

    def ls_todo(self, context: Context):
        context.log_task_table_from_statuses(context.profile.get_todo_statuses())

    def ls_doing(self, context: Context):
        context.log_task_table_from_statuses(context.profile.get_doing_statuses())

    def ls_done(self, context: Context):
        context.log_task_table_from_statuses(context.profile.get_done_statuses())

    def set_status(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        set_status = context.profile.set_status(task, context.args.get("status"))
        if not set_status:
            return context.logger.log_error("Invalid status provided")

        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)

    def set_description(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        task.description = ' '.join(context.args.get("description"))

        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)

    def set_link(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        task.link = context.args.get("link")

        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)

    def set_priority(context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        passed, priority = parse_priority_from_arg(context.args.get("priority"))
        if not passed:
            return context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")

        task.priority = priority

        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)

    def add_tag(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        tags = context.args.get("tags")

        for t in tags:
            if t not in task.tags:
                task.tags.append(t)

        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)

    def rm_tag(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        tags = context.args.get("tags")

        for t in tags:
            if t in task.tags:
                task.tags.remove(t)

        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)

    def add_assigned(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        assignees = context.args.get("assignee")

        for a in assignees:
            if a not in task.assigned_to:
                task.assigned_to.append(a)

        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)

    def rm_assigned(self, context: Context):
        task = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return context.logger.log_error("Task not found")

        assignees = context.args.get("assignee")

        for a in assignees:
            if a in task.assigned_to:
                task.assigned_to.remove(a)

        context.profile.save()
        context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            context.log_task(task)
