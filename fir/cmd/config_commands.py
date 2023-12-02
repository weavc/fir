from collections import defaultdict
from tabulate import tabulate
from termcolor import colored

from fir.cmd.cmd_builder import CmdBuilder
from fir.context import Context


class ConfigHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = "config"
    aliases = []


@ConfigHandlers.command("get", aliases=["g"])
@ConfigHandlers.add_positional("config_name")
def get_config_value(context: Context):
    value = context.profile.get("config").get(context.args.get("config_name"))
    context.logger.log(f"{context.args.get('config_name')}: {value}")


@ConfigHandlers.command("set", aliases=["s"])
@ConfigHandlers.add_positional("config_value")
@ConfigHandlers.add_positional("config_name")
def set_config_value(context: Context):
    context.profile.get("config")[context.args.get("config_name")] = context.args.get("config_value")
    context.data.update_profile(context.profile.get("name"), context.profile)
    context.logger.log_success(f"Updated config {context.args.get('config_name')}")


@ConfigHandlers.command("clear", aliases=["rm", "remove"])
@ConfigHandlers.add_positional("config_name")
def remove_config_value(context: Context):
    context.profile.get("config")[context.args.get("config_name")] = None
    context.data.update_profile(context.profile.get("name"), context.profile)
    context.logger.log_success(f"Removed config {context.args.get('config_name')}")


@ConfigHandlers.command("ls", aliases=["list"])
def list_config_values(context: Context):
    table = []
    for key, value in context.profile.get("config").items():
        table.append([key, value])

    context.logger.log(tabulate(table,
                                headers=[f"{colored('Name', 'light_green', attrs=['bold'])}",
                                         f"{colored('Value', 'light_green', attrs=['bold'])}"]))
