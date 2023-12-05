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
        
        self.register_commands(*[t for t in self.map()])

    def map(self) -> list[Cmd]:
        return [
            # Cmd("new",
            #     "Add a new task.",
            #     aliases=["add"],
            #     args=[pm["task_name"].with_overrides(nargs="+")],
            #     optionals=[pm["status"], pm["due"], pm["link"], pm["priority"], pm["description"]],
            #     func=self.create_task),
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
                optionals=[pm["status"], pm["task_name"], pm["assignee"], pm["tags"]],
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
            Cmd("todo", 
                description="List all todo tasks.", 
                func=self.ls_todo, 
                optionals=[pm["status"], pm["task_name"], pm["assignee"], pm["tags"]]),
            Cmd("doing", 
                aliases=["prog"], 
                description="List all in progress tasks.", 
                func=self.ls_doing, 
                optionals=[pm["status"], pm["task_name"], pm["assignee"], pm["tags"]]),
            Cmd("done", 
                description="List all done/completed tasks.", 
                func=self.ls_done, 
                optionals=[pm["status"], pm["task_name"], pm["assignee"], pm["tags"]]),
        ]

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

    def ls(self, category: StatusTypes = None):
        tasks = []
        for task in self.context.profile.data.tasks:
            if self.context.args.get("status") and task.status != self.context.args.get("status"):
                continue
            if self.context.args.get("task_name") and not self.context.args.get("task_name").lower() in task.name.lower():
                continue
            if self.context.args.get("assignee") and self.context.args.get("assignee") not in task.assigned_to:
                continue
            if self.context.args.get("tags") and self.context.args.get("tags") not in task.tags:
                continue
            
            c, _ = self.context.profile.check_status_type(task.status) 

            if self.context.profile.try_get_config_value_bool("enable.ls.hide_done_tasks"):
                if  c == "done":
                    continue
            if category and category != c:
                continue

            tasks.append(task)

        self.context.log_task_table(tasks)

    def ls_todo(self):
        return self.ls("todo")

    def ls_doing(self):
        return self.ls("doing")

    def ls_done(self):
        return self.ls("done")

    def set_status(self):
        task = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error("Task not found")

        set_status = self.context.profile.set_status(task, self.context.args.get("status"))
        if not set_status:
            return self.context.logger.log_error("Invalid status provided")

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.log_task(task)

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
