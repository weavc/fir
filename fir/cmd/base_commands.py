from collections import defaultdict
from datetime import date, datetime
from tabulate import tabulate
from termcolor import colored

from fir.cmd.cmd_builder import CmdBuilder
from fir.context import Context
from fir.data.defaults import default_task_struct
from fir.helpers.dates import datetime_to_date_string, str_to_date_string

class CommandHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = None
    aliases = []
    
@CommandHandlers.command("create", aliases=["c", "add"])
@CommandHandlers.add_positional("task_name", nargs="+")
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("due", "--due")
def create_task(context: Context):
    tasks = context.profile.get("tasks")
    if tasks is None:
        tasks = []

    status = context.profile.get("config").get("defaults.status")
    if context.args.get("status") is not None:
        status = context.args.get("status")

    due = ""
    if context.args.get("due"):
        try:
            due = str_to_date_string(context.args.get("due"))
        except ValueError:
            return context.logger.log_error(f"Unable to parse date from due date")
        
    task_name = ' '.join(context.args.get("task_name"))
    task = default_task_struct(task_name, [], status, due=due)
    tasks.append(task)
    context.data.update_profile(context.profile.get("name"), context.profile)

    return context.logger.log_success(f"Added task {task_name} to profile {context.profile.get('name')}")

@CommandHandlers.command("modify", aliases=["mod", "m", "edit"])
@CommandHandlers.add_positional("task_id")
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("tag", "--tag", "-t")
@CommandHandlers.add_optional("name", "--name", "-n")
@CommandHandlers.add_optional("due", "--due")
def modify_task(context: Context):
    tasks = context.profile.get("tasks")
    if tasks is None:
        return context.logger.log_error("Task not found")
    
    for task in tasks:
        if task.get("id").startswith(context.args.get("task_id")):
            if context.args.get("status") is not None:
                task["status"] = context.args.get("status")
            if context.args.get("tag") is not None:
                if context.args.get("tag") in task["tags"]:
                    task["tags"].remove(context.args.get("tag"))
                else:
                    task["tags"].append(context.args.get("tag"))
            if context.args.get("name") is not None:
                task["name"] = context.args.get("name")
            if context.args.get("due"):
                try:
                    due = str_to_date_string(context.args.get("due"))
                    task["due"] = due
                except ValueError:
                    return context.logger.log_error(f"Unable to parse date from due date")

            task["modified"] = datetime_to_date_string(datetime.now())
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
        if task.get("tags"):
            tags = ', '.join(task.get("tags"))

        due = ""
        if task.get("due"):
            due = task.get("due")
        
        table.append([
            task.get("id"), 
            task.get("name"),
            task.get("status"), 
            due, tags])

    context.logger.log(tabulate(table, 
        headers=[f"{colored('Id', 'light_green', attrs=['bold'])}", 
                 f"{colored('Task', 'light_green', attrs=['bold'])}", 
                 f"{colored('Status', 'light_green', attrs=['bold'])}", 
                 f"{colored('Tags', 'light_green', attrs=['bold'])}",
                 f"{colored('Due', 'light_green', attrs=['bold'])}"
                 ]))