from cmd import Cmd

import tabulate
from termcolor import colored
from fir.cmd.builder import CmdBuilder
from fir.context import Context
from fir.utils.parse import parse_priority_from_arg
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
            .with_optional(pm["color"], pm["order"])\
            .with_flag(pm["hide_status"])

        self.register("hide", self.hide_status, description="Hide or show tasks with this status.")\
            .with_positional(pm["status"])
        
        self.register("rm", self.rm_status, description="Remove given status.")\
            .with_positional(pm["status"])
        
        self.register("order", self.set_order, description="Set the order value of the given status.")\
            .with_positional(pm["status"], pm["order"])
        
        self.register("color", self.set_colour_status, aliases=["colour"], description="Hide or show tasks with this status.")\
            .with_positional(pm["status"], pm["color"])
        
        self.register("list", self.list_status, description="List avaiable statuses.", aliases=["ls"])

    def new_status(self):
        color = self.context.get_arg("color", "light_blue")
        hide_status = self.context.get_arg("hide_status", True)
        passed, order = parse_priority_from_arg(self.context.get_arg("order"), 600)
        if not passed:
            return self.context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")

        status = StatusDto(self.context.args.get("status"), color, order=order, hide_by_default=hide_status)
        self.context.profile.data.statuses.append(status)

        self.context.profile.save()
        self.context.logger.log_success(f"Added status \"{status.name}\"")

    def set_colour_status(self):
        status = self.context.profile.get_status_by_name(self.context.args.get("status"))
        if status is None:
            return self.context.logger.log_error("Could not find status.")

        status.color = self.context.get_arg("color", "light_blue")

        self.context.profile.save()
        self.context.logger.log_success(f"Set color of status to \"{status.color}\"")

    def set_order(self):
        status = self.context.profile.get_status_by_name(self.context.args.get("status"))
        if status is None:
            return self.context.logger.log_error("Could not find status.")
        
        passed, order = parse_priority_from_arg(self.context.get_arg("order"), 600)
        if not passed:
            return self.context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")

        status.order = order

        self.context.profile.save()
        self.context.logger.log_success(f"Set order value of status \"{status.name}\" to {status.order}.")

    def hide_status(self):
        status = self.context.profile.get_status_by_name(self.context.args.get("status"))
        if status is None:
            return self.context.logger.log_error("Could not find status.")

        status.hide_by_default = not status.hide_by_default

        self.context.profile.save()
        self.context.logger.log_success(f"Set hide status to \"{status.hide_by_default}\"")

    def rm_status(self):
        status = self.context.profile.get_status_by_name(self.context.args.get("status"))
        if status is None:
            return self.context.logger.log_error("Could not find status.")

        self.context.profile.data.statuses.remove(status)

        self.context.profile.save()
        self.context.logger.log_success(f"Removed status \"{status.name}\"")

    def list_status(self):
        table = []
        statuses = sorted(self.context.profile.data.statuses, key=lambda s: s.order)
        for s in statuses:
            table.append([s.name, colored(s.color, s.color), s.order, s.hide_by_default])

        headers = [f"{colored('Name', 'light_blue', attrs=['bold'])}",
                    f"{colored('Color', 'light_blue', attrs=['bold'])}",
                    f"{colored('Order', 'light_blue', attrs=['bold'])}",
                    f"{colored('Hide', 'light_blue', attrs=['bold'])}"]

        tab = tabulate.tabulate(table, headers=headers)

        self.context.logger.log(tab)