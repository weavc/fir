from cmd import Cmd
from fir.cmd.builder import CmdBuilder
from fir.context import Context
from fir.utils.parse import parse_priority_from_arg
from fir.types.parameters import ParameterMap as pm


class SetHandlers(CmdBuilder):
    name = "set"
    aliases = []
    cmds: dict[str, Cmd] = {}

    context: Context

    def __init__(self, context: Context):
        self.context = context

        self.register("status", self.set_status, description="Set the status of a task.")\
            .with_positional(pm["task_id"], pm["status"])

        self.register("priority", self.set_priority, description="Set priority level of a task (1-999). Default: 100.")\
            .with_positional(pm["task_id"], pm["priority"])

        self.register("description", self.set_description, aliases=["desc"],
                      description="Add a description to a task.")\
            .with_positional(pm["task_id"], pm["description"].with_overrides(nargs="+"))

        self.register(
            "link",
            self.set_link,
            aliases=[],
            description="Add a link to a task. i.e. https://github.com/weavc/fir/issues/1")\
            .with_positional(pm["task_id"], pm["link"])

    def set_status(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        set_status = self.context.profile.set_status(task, self.context.args.get("status"))
        if not set_status:
            return self.context.logger.log_error("Invalid status provided")

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def set_link(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        task.link = self.context.args.get("link")

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def set_priority(self, context: Context):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        passed, priority = parse_priority_from_arg(self.context.args.get("priority"))
        if not passed:
            return self.context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")

        task.priority = priority

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)

    def set_description(self):
        task, err = self.context.profile.get_task(self.context.args.get("task_id"))
        if task is None:
            return self.context.logger.log_error(err)

        task.description = ' '.join(self.context.args.get("description"))

        self.context.profile.save()
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)
