 so rather than like json or whatever you can use that.from cmd import Cmd
from fir.cmd.builder import CmdBuilder
from fir.context import Context
from fir.handlers import SetHandlers as set
from fir.types.parameters import ParameterMap as pm


class SetHandlers(CmdBuilder):
    name = "set"
    aliases = []
    cmds: dict[str, Cmd] = {}

    context: Context

    def __init__(self, context: Context, register = True):
        self.context = context

        if not register:
            return
        
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

    def log_updated(self, task):
        self.context.logger.log_success(f"Updated task {task.name} [{task.id}]")
        if self.context.profile.try_get_config_value_bool("enable.log_task_post_modify"):
            self.context.logging.profile.log_task(task)


    def set_status(self):
        task, err = set.status(self.context)
        if err is not None:
            return self.context.logger.log_error(err.message)

        self.log_updated(task)

    def set_link(self):
        task, err = set.link(self.context)
        if err is not None:
            return self.context.logger.log_error(err.message)
        
        self.log_updated(task)
        
    def set_priority(self):
        task, err = set.priority(self.context.args.get("task_id"))
        if err is not None:
            return self.context.logger.log_error(err.message)
        
        self.log_updated(task)

    def set_description(self):
        task, err = set.description(self.context)
        if err is not None:
            return self.context.logger.log_error(err.message)
        
        self.log_updated(task)