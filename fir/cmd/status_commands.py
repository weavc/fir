from cmd import Cmd

import tabulate
from termcolor import colored
from fir.cmd.builder import CmdBuilder
from fir.context import Context
from fir.utils.parse import parse_priority_from_arg
from fir.types.dtos import StatusDto
from fir.types.parameters import ParameterMap as pm
from fir.handlers import status, set

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

        self.register(
            "color",
            self.set_colour_status,
            aliases=["colour"],
            description="Hide or show tasks with this status.")\
            .with_positional(pm["status"], pm["color"])

        self.register("list", self.list_status, description="List avaiable statuses.", aliases=["ls"])

    def new_status(self):
        s, err = s.new(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        self.context.logger.log_success(f"Added status \"{s.name}\"")

    def set_colour_status(self):
        s, err = status.colour(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        self.context.logger.log_success(f"Set color of status to \"{s.color}\"")

    def set_order(self):
        s, err = status.order(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        self.context.logger.log_success(f"Set order value of status \"{s.name}\" to {s.order}.")

    def hide_status(self):
        s, err = status.hide(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        self.context.logger.log_success(f"Set hide status to \"{s.hide_by_default}\"")

    def rm_status(self):
        s, err = status.rm(self.context)
        if err is not None:
            return self.context.logger.log_error(err)
        
        self.context.logger.log_success(f"Removed status \"{s.name}\"")

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
