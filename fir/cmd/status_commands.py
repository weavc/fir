from cmd import Cmd
from fir.cmd.builder import CmdBuilder
from fir.context import Context
from fir.helpers.parse import parse_priority_from_arg
from fir.types.dtos import StatusDto
from fir.types.parameters import ParameterMap as pm

class StatusHandlers(CmdBuilder):
    name = "status"
    aliases = []
    cmds: dict[str, Cmd] = {}

    context: Context

    def __init__(self, context: Context):
        self.context = context
        
        self.register("new", self.new_status, description="Set the status of a task.")\
            .with_positional(pm["status"])\
            .with_optional(pm["color"], pm["priority"])\
            .with_flag(pm["hide_status"])
    
        self.register("hide", self.hide_status, description="Hide or show tasks with this status.")\
            .with_positional(pm["status"])

    def new_status(self):
        color = self.context.args.get("color", "light_blue")
        hide_status = self.context.args.get("hide_status", False)
        passed, priority = parse_priority_from_arg(self.context.args.get("priority"), 600)
        if not passed:
            return self.context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")

        status = StatusDto(self.context.args.get("status"), color, priority=priority, hide_by_default=hide_status)

        self.context.profile.data.statuses.append(status)

        self.context.profile.save()
        self.context.logger.log_success(f"Added status \"{status.name}\"")

    def hide_status(self):
        status = self.context.profile.get_status_by_name(self.context.args.get("status"))
        if status is None:
            return self.context.logger.log_error("Could not find status.")

        status.hide_by_default = not status.hide_by_default

        self.context.profile.save()
        self.context.logger.log_success(f"Set hide status to \"{status.hide_by_default}\"")
