from collections import defaultdict
from datetime import date, datetime
from tabulate import tabulate
from termcolor import colored

from fir.cmd.cmd_builder import CmdBuilder
from fir.context import Context
from fir.data.defaults import default_task_struct
from fir.helpers import generate_id
from fir.helpers.dates import datetime_to_date_string, str_to_date_string
from fir.model.dtos import TaskDto


class CommandHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = None
    aliases = []


@CommandHandlers.command("create", aliases=["c", "add"])
@CommandHandlers.add_positional("task_name", nargs="+")
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("due", "--due")
def create_task(context: Context):
    status = context.profile.data.config.get("defaults.status")
    if context.args.get("status"):
        status = context.args.get("status")

    due = __parse_date_from_arg(context, context.args.get("due"))

    task_name = ' '.join(context.args.get("task_name"))
    task = TaskDto(generate_id(), task_name, status, due=due)
    context.profile.data.tasks.append(task)
    context.profile.save()

    context.logger.log_success(
        f"Added task {task.name} [{task.id}] to profile {context.profile.data.name}")
    __log_task(context, task)


@CommandHandlers.command("modify", aliases=["mod", "m", "edit"])
@CommandHandlers.add_positional("task_id")
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("tag", "--tag", "-t")
@CommandHandlers.add_optional("name", "--name", "-n")
@CommandHandlers.add_optional("due", "--due")
def modify_task(context: Context):
    task = next((x for x in context.profile.data.tasks if x.id.startswith(
        context.args.get("task_id"))), None)
    if task is None:
        return context.logger.log_error("Task not found")

    if context.args.get("status") is not None:
        task.status = context.args.get("status")
    if context.args.get("tag") is not None:
        if context.args.get("tag") in task.tags:
            task.tags.remove(context.args.get("tag"))
        else:
            task.tags.append(context.args.get("tag"))
    if context.args.get("name") is not None:
        task.name = context.args.get("name")
    if context.args.get("due"):
        task.due = __parse_date_from_arg(context, context.args.get("due"))

    task.modified = datetime_to_date_string(datetime.now())
    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    __log_task(context, task)


@CommandHandlers.command("remove", aliases=["rm"])
@CommandHandlers.add_positional("task_id")
def remove_task(context: Context):
    task = next((x for x in context.profile.data.tasks if x.id.startswith(
        context.args.get("task_id"))), None)
    if task is None:
        return context.logger.log_error("Task not found")

    context.profile.data.tasks.remove(task)
    context.profile.save()

    return context.logger.log_success(f"Removed task {task.name} [{task.id}]")


@CommandHandlers.command("info", aliases=["i"])
@CommandHandlers.add_positional("task_id")
def task_info(context: Context):
    task = next((x for x in context.profile.data.tasks if x.id.startswith(
        context.args.get("task_id"))), None)
    if task is None:
        return context.logger.log_error("Task not found")

    __log_task(context, task)


@CommandHandlers.command("list", aliases=["ls"])
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("name", "--name", "-n")
@CommandHandlers.add_optional("id", "--id", "-i")
def ls(context: Context):
    table = []
    for task in context.profile.data.tasks:
        if context.args.get("status") is not None and task.status != context.args.get("status"):
            continue
        if context.args.get("id") is not None and not task.id.startswith(context.args.get("id")):
            continue
        if context.args.get("name") is not None and not context.args.get("name").lower() in task.name.lower():
            continue

        table.append([
            colored(task.id, 'light_grey'),
            task.name,
            task.status,
            task.due,
            ', '.join(task.tags)])

    context.logger.log(tabulate(table,
                                headers=[f"{colored('Id', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Task', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Status', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Due', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Tags', 'light_blue', attrs=['bold'])}"
                                         ]))


def __log_task(context: Context, task: TaskDto):
    context.logger.log(
        f"{colored('Name', 'light_blue', attrs=['bold'])}: {task.name}")
    context.logger.log(
        f"{colored('Id', 'light_blue', attrs=['bold'])}: {task.id}")
    context.logger.log(
        f"{colored('Status', 'light_blue', attrs=['bold'])}: {task.status}")
    context.logger.log(
        f"{colored('Due', 'light_blue', attrs=['bold'])}: {task.due}")
    context.logger.log(
        f"{colored('Tags', 'light_blue', attrs=['bold'])}: {', '.join(task.tags)}")


def __parse_date_from_arg(context: Context, date: str):
    dt = ""
    if date:
        try:
            dt = str_to_date_string(date)
        except ValueError:
            return context.logger.log_error(f"Unable to parse date from due date")

    return dt
