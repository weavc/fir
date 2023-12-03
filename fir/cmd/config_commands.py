from collections import defaultdict
from typing import get_args
from tabulate import tabulate
from termcolor import colored

from fir.builder import Cmd, CmdBuilderV2
from fir.context import Context
from fir.types import ConfigOptions, ConfigOptionsMap
from fir.types.parameters import ParameterMap


class ConfigHandlers(CmdBuilderV2):
    name = "config"
    aliases = []


@ConfigHandlers.command(Cmd("get", aliases=["g"], description="Get value for config option."))
@ConfigHandlers.add_positional(ParameterMap["config_name"])
def get_config_value(context: Context):
    if context.args.get("config_name") not in get_args(ConfigOptions):
        return context.invalid_config_option(context)

    value = context.profile.data.config.get(context.args.get("config_name"))
    context.logger.log(f"{context.args.get('config_name')}: {value}")


@ConfigHandlers.command(Cmd("set", aliases=["s"], description="Set value for config option."))
@ConfigHandlers.add_positional(ParameterMap["config_value"], ParameterMap["config_name"])
def set_config_value(context: Context):
    if context.args.get("config_name") not in get_args(ConfigOptions):
        return context.invalid_config_option(context)

    context.profile.data.config[context.args.get("config_name")] = context.args.get("config_value")
    context.profile.save()
    context.logger.log_success(f"Updated config {context.args.get('config_name')}")


@ConfigHandlers.command(Cmd("rm", description="Remove value for a config option."))
@ConfigHandlers.add_positional(ParameterMap["config_name"])
def remove_config_value(context: Context):
    if context.args.get("config_name") not in get_args(ConfigOptions):
        return context.invalid_config_option(context)

    context.profile.data.config.pop(context.args.get("config_name"))
    context.profile.save()
    context.logger.log_success(f"Removed config {context.args.get('config_name')}")


@ConfigHandlers.command(Cmd("ls", aliases=["list"], description="List all set config options."))
def list_config_values(context: Context):
    table = []
    for key, value in context.profile.data.config.items():
        table.append([key, value])

    context.logger.log(tabulate(table,
                                headers=[f"{colored('Name', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Value', 'light_blue', attrs=['bold'])}"]))


@ConfigHandlers.command(Cmd("options", aliases=["opt", "opts"], description="List all available config options."))
def list_config_options(context: Context):
    table = []
    for key in get_args(ConfigOptions):
        map = ConfigOptionsMap.get(key)
        table.append([map.name, map.description, map.example])

    context.logger.log(tabulate(table,
                                headers=[f"{colored('Name', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Description', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Example', 'light_blue', attrs=['bold'])}"]))
