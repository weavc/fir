from typing import get_args
from tabulate import tabulate
from termcolor import colored

from fir.cmd.builder import Cmd, CmdBuilder
from fir.context import Context
from fir.types.config_options import ConfigOptions, ConfigOptionsMap
from fir.types.parameters import ParameterMap as pm


class ConfigHandlers(CmdBuilder):
    name = "config"
    aliases = []
    cmds: dict[str, Cmd] = {}

    context: Context

    def __init__(self, context: Context):
        self.context = context
        self.register("get", self.get_config_value, description="Get value for config option.")\
            .with_positional(pm["config_name"])

        self.register("set", self.set_config_value, description="Set value for config options.")\
            .with_positional(pm["config_name"], pm["config_value"])
        
        self.register("rm", self.remove_config_value, description="Remove value for config options.")\
            .with_positional(pm["config_name"])
        
        self.register("list", self.list_config_values, description="List all set config options.", aliases=["ls"])

        self.register("options", self.list_config_options, description="List all available config options.", aliases=["opts", "opt"])

    def get_config_value(self):
        if self.context.args.get("config_name") not in get_args(ConfigOptions):
            return self.context.invalid_config_option()

        value = self.context.profile.data.config.get(self.context.args.get("config_name"))
        self.context.logger.log(f"{self.context.args.get('config_name')}: {value}")

    def set_config_value(self):
        if self.context.args.get("config_name") not in get_args(ConfigOptions):
            return self.context.invalid_config_option()

        self.context.profile.data.config[self.context.args.get("config_name")] = self.context.args.get("config_value")
        self.context.profile.save()
        self.context.logger.log_success(f"Updated config {self.context.args.get('config_name')}")

    def remove_config_value(self):
        if self.context.args.get("config_name") not in get_args(ConfigOptions):
            return self.context.invalid_config_option()

        self.context.profile.data.config.pop(self.context.args.get("config_name"))
        self.context.profile.save()
        self.context.logger.log_success(f"Removed config {self.context.args.get('config_name')}")

    def list_config_values(self):
        table = []
        for key, value in self.context.profile.data.config.items():
            table.append([key, value])

        self.context.logger.log(tabulate(table,
                                         headers=[f"{colored('Name', 'light_blue', attrs=['bold'])}",
                                                  f"{colored('Value', 'light_blue', attrs=['bold'])}"]))

    def list_config_options(self):
        table = []
        for key in get_args(ConfigOptions):
            map = ConfigOptionsMap.get(key)
            table.append([map.name, map.description, map.example])

        self.context.logger.log(tabulate(table,
                                         headers=[f"{colored('Name', 'light_blue', attrs=['bold'])}",
                                                  f"{colored('Description', 'light_blue', attrs=['bold'])}",
                                                  f"{colored('Example', 'light_blue', attrs=['bold'])}"]))
