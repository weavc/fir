from collections import defaultdict
from datetime import datetime
from tabulate import tabulate
from termcolor import colored

from fir.cmd.cmd_builder import CmdBuilder
from fir.context import Context
from fir.data.defaults import default_task_struct

class CommandHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = None
    aliases = []
    
@CommandHandlers.command("create", aliases=["c", "add"])
@CommandHandlers.add_positional("task_name", nargs="+")
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("tags", "--tags", "-t", nargs="+")
def create_task(context: Context):
    tasks = context.profile.get("tasks")
    if tasks is None:
        tasks = []

    status = context.profile.get("config").get("defaults.status")
    if context.args.get("status") is not None:
        status = context.args.get("status")

    task_name = ' '.join(context.args.get("task_name"))
    task = default_task_struct(task_name, context.args.get("tags"), status)
    tasks.append(task)
    context.data.update_profile(context.profile.get("name"), context.profile)

    context.logger.log_success(f"Added task {task_name} to profile {context.profile.get('name')}")

@CommandHandlers.command("modify", aliases=["mod", "m", "edit"])
@CommandHandlers.add_positional("task_id")
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("tags", "--tags", "-t", nargs="+")
@CommandHandlers.add_optional("name", "--name", "-n")
def modify_task(context: Context):
    tasks = context.profile.get("tasks")
    if tasks is None:
        return context.logger.log_error("Task not found")
    
    for task in tasks:
        if task.get("id").startswith(context.args.get("task_id")):
            if context.args.get("status") is not None:
                task["status"] = context.args.get("status")
            if context.args.get("tags") is not None:
                task["tags"] = context.args.get("tags")
            if context.args.get("name") is not None:
                task["name"] = context.args.get("name")
            context.data.update_profile(context.profile.get("name"), context.profile)
            return context.logger.log_success(f"Updated task {task.get('id')}")
    
    return context.logger.log_error("Task not found")

@CommandHandlers.command("remove", aliases=["rm"])
@CommandHandlers.add_positional("task_id")
def remove_task(context: Context):
    tasks = context.profile.get("tasks")
    if tasks is None:
        return context.logger.log_error("Task not found")
    for task in tasks:
        if task.get("id").startswith(context.args.get("task_id")):
            tasks.remove(task)
            context.data.update_profile(context.profile.get("name"), context.profile)
            return context.logger.log_success(f"Removed task {task.get('id')}")
    
    return context.logger.log_error("Task not found")

@CommandHandlers.command("info", aliases=["i"])
@CommandHandlers.add_positional("task_id")
def task_info(context: Context):
    task = context.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    for name, value in task.items():
        context.logger.log(f"{colored(name, 'light_green', attrs=['bold'])}: {value}")

@CommandHandlers.command("list", aliases=["ls"])
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("name", "--name", "-n")
@CommandHandlers.add_optional("id", "--id", "-i")
def ls(context: Context):
    table = []
    for task in context.profile.get("tasks"):
        if context.args.get("status") is not None and task.get("status") != context.args.get("status"):
            continue
        if context.args.get("id") is not None and not task.get("id").startswith(context.args.get("id")):
            continue
        if context.args.get("name") is not None and not context.args.get("name").lower() in task.get("name").lower():
            continue

        tags = ""
        if task.get("tags") is not None:
            tags = ', '.join(task.get("tags"))

        due = ""
        if task.get("due") is not None:
            due = datetime.fromisoformat(task.get("due")).strftime("%d/%m/%Y")
        
        table.append([
            task.get("id"), 
            task.get("name"),
            task.get("status"), 
            tags, due])

    context.logger.log(tabulate(table, 
        headers=[f"{colored('Id', 'light_green', attrs=['bold'])}", 
                 f"{colored('Task', 'light_green', attrs=['bold'])}", 
                 f"{colored('Status', 'light_green', attrs=['bold'])}", 
                 f"{colored('Tags', 'light_green', attrs=['bold'])}",
                 f"{colored('Due', 'light_green', attrs=['bold'])}"
                 ]))