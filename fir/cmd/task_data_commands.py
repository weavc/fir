from collections import defaultdict
from tabulate import tabulate
from termcolor import colored

from fir.cmd.cmd_builder import CmdBuilder
from fir.context import Context

class TaskDataHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = "data"
    aliases = []

@TaskDataHandlers.command("get", aliases=["g"])
@TaskDataHandlers.add_positional("field_name")
@TaskDataHandlers.add_positional("task_id")
def get_data_value(context: Context):
    task = context.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")
    
    data = task.get("data")
    if data is None:
        return context.logger.log_error("Field not found")
    
    value = data.get(context.args.get("field_name"))
    if value is None:
        return context.logger.log_error("Field not found")
    
    context.logger.log(f"{context.args.get('field_name')}: {value}")

@TaskDataHandlers.command("set", aliases=["s"])
@TaskDataHandlers.add_positional("field_value")
@TaskDataHandlers.add_positional("field_name")
@TaskDataHandlers.add_positional("task_id")
def set_data_value(context: Context):
    task = context.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    data = task.get("data")
    if data is None:
        task["data"] = {}

    task["data"][context.args.get("field_name")] = context.args.get("field_value")
    context.data.update_profile(context.profile.get("name"), context.profile)
    context.logger.log_success(f"Updated task {task.get('id')}")

@TaskDataHandlers.command("clear", aliases=["rm", "remove"])
@TaskDataHandlers.add_positional("field_name")
@TaskDataHandlers.add_positional("task_id")
def remove_config_value(context: Context):
    task = context.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")
    
    data = task.get("data")
    if data is None:
        task["data"] = {}

    task["data"].pop(context.args.get("field_name"))
    context.data.update_profile(context.profile.get("name"), context.profile)
    context.logger.log_success(f"Updated task {task.get('id')}")

@TaskDataHandlers.command("ls", aliases=["list"])
@TaskDataHandlers.add_positional("task_id")
def list_config_values(context: Context):
    task = context.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")
    
    data = task.get("data")
    if data is None:
        task["data"] = {}
    
    table = []
    for key, value in task.get("data").items():
        table.append([key, value])

    context.logger.log(tabulate(table, 
        headers=[f"{colored('Name', 'light_green', attrs=['bold'])}", 
                 f"{colored('Value', 'light_green', attrs=['bold'])}"]))