from collections import defaultdict
from datetime import datetime


from fir.cmd.cmd_builder import CmdBuilder
from fir.context import Context
from fir.helpers import generate_id
from fir.helpers.commands import log_task, log_task_table, log_task_table_from_statuses, parse_date_from_arg, parse_priority_from_arg
from fir.helpers.dates import datetime_to_date_string
from fir.types.dtos import TaskDto


class CommandHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = None
    aliases = []


@CommandHandlers.command("new", aliases=["add"])
@CommandHandlers.add_positional("task_name", nargs="+")
@CommandHandlers.add_optional("status", "--status")
@CommandHandlers.add_optional("due", "--due")
@CommandHandlers.add_optional("link", "--link")
@CommandHandlers.add_optional("priority", "--priority")
@CommandHandlers.add_optional("description", "--desc", "--description")
def create_task(context: Context):
    status = context.profile.data.config.get("status.default", "")
    if context.args.get("status"):
        status = context.args.get("status")

    due = parse_date_from_arg(context, context.args.get("due"))

    task_name = ' '.join(context.args.get("task_name"))
    task = TaskDto(generate_id(), task_name, due=due)

    set_status = context.profile.set_status(task, status)
    if not set_status:
        return context.logger.log_error("Invalid status provided")
    
    if (context.args.get("priority")):
        passed, priority = parse_priority_from_arg(context.args.get("priority"))
        if not passed:
            return context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")
        task.priority = priority
    if context.args.get("description"):
        task.description = context.args.get("description")
    if context.args.get("link"):
        task.link = context.args.get("link")

    context.profile.data.tasks.append(task)
    context.profile.save()

    context.logger.log_success(
        f"Added task {task.name} [{task.id}] to profile {context.profile.data.name}")
    log_task(context, task)


@CommandHandlers.command("mod", aliases=["edit"])
@CommandHandlers.add_positional("task_id")
@CommandHandlers.add_optional("status", "--status")
@CommandHandlers.add_optional("name", "--name")
@CommandHandlers.add_optional("due", "--due")
@CommandHandlers.add_optional("link", "--link")
@CommandHandlers.add_optional("priority", "--priority")
@CommandHandlers.add_optional("description", "--desc", "--description")
def modify_task(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    if context.args.get("status") is not None:
        set_status = context.profile.set_status(task, context.args.get("status"))
        if not set_status:
            return context.logger.log_error("Invalid status provided")
    if context.args.get("name") is not None:
        task.name = context.args.get("name")
    if context.args.get("due"):
        task.due = parse_date_from_arg(context, context.args.get("due"))
    if (context.args.get("priority")):
        passed, priority = parse_priority_from_arg(context.args.get("priority"))
        if not passed:
            return context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")
        task.priority = priority
    if context.args.get("description"):
        task.description = context.args.get("description")
    if context.args.get("link"):
        task.link = context.args.get("link")

    task.modified = datetime_to_date_string(datetime.now())
    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)


@CommandHandlers.command("rm")
@CommandHandlers.add_positional("task_id")
def remove_task(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    context.profile.data.tasks.remove(task)
    context.profile.save()

    return context.logger.log_success(f"Removed task {task.name} [{task.id}]")


@CommandHandlers.command("info")
@CommandHandlers.add_positional("task_id")
def task_info(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    log_task(context, task)


@CommandHandlers.command("list", aliases=["ls"])
@CommandHandlers.add_optional("status", "--status", "-s")
@CommandHandlers.add_optional("name", "--name", "-n")
@CommandHandlers.add_optional("id", "--id", "-i")
def ls(context: Context):
    tasks = []
    for task in context.profile.data.tasks:
        if context.args.get("status") is not None and task.status != context.args.get("status"):
            continue
        if context.args.get("id") is not None and not task.id.startswith(context.args.get("id")):
            continue
        if context.args.get("name") is not None and not context.args.get("name").lower() in task.name.lower():
            continue

        if context.profile.try_get_config_value_bool("enable.ls.hide_done_tasks"):
            if context.profile.check_status_type(task.status) == "done":
                continue

        tasks.append(task)

    log_task_table(context, tasks)


@CommandHandlers.command("todo")
def ls_todo(context: Context):
    log_task_table_from_statuses(context, context.profile.get_todo_statuses())


@CommandHandlers.command("doing", aliases=["prog"])
def ls_doing(context: Context):
    log_task_table_from_statuses(context, context.profile.get_doing_statuses())


@CommandHandlers.command("done")
def ls_done(context: Context):
    log_task_table_from_statuses(context, context.profile.get_done_statuses())


@CommandHandlers.command("status")
@CommandHandlers.add_positional("status")
@CommandHandlers.add_positional("task_id")
def set_status(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    set_status = context.profile.set_status(task, context.args.get("status"))
    if not set_status:
        return context.logger.log_error("Invalid status provided")

    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)


@CommandHandlers.command("description", aliases=["desc"])
@CommandHandlers.add_positional("description", nargs="+")
@CommandHandlers.add_positional("task_id")
def set_description(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    task.description = ' '.join(context.args.get("description"))

    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)


@CommandHandlers.command("link", aliases=["ln"])
@CommandHandlers.add_positional("link")
@CommandHandlers.add_positional("task_id")
def set_link(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    task.link = context.args.get("link")

    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)


@CommandHandlers.command("priority")
@CommandHandlers.add_positional("priority")
@CommandHandlers.add_positional("task_id")
def set_priority(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")
    
    passed, priority = parse_priority_from_arg(context.args.get("priority"))
    if not passed:
        return context.logger.log_error("Invalid priorty value. Must be an integer and between 1 - 999.")

    task.priority = priority

    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)


@CommandHandlers.command("tag")
@CommandHandlers.add_positional("tags", nargs="+")
@CommandHandlers.add_positional("task_id")
def add_tag(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    tags = context.args.get("tags")

    for t in tags:
        if t not in task.tags:
            task.tags.append(t)

    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)


@CommandHandlers.command("rmtag", aliases=["rmt"])
@CommandHandlers.add_positional("tags", nargs="+")
@CommandHandlers.add_positional("task_id")
def rm_tag(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    tags = context.args.get("tags")

    for t in tags:
        if t in task.tags:
            task.tags.remove(t)

    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)


@CommandHandlers.command("assign")
@CommandHandlers.add_positional("assignee", nargs="+")
@CommandHandlers.add_positional("task_id")
def add_assigned(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    assignees = context.args.get("assignee")

    for a in assignees:
        if a not in task.assigned_to:
            task.assigned_to.append(a)

    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)


@CommandHandlers.command("unassign")
@CommandHandlers.add_positional("assignee", nargs="+")
@CommandHandlers.add_positional("task_id")
def rm_assigned(context: Context):
    task = context.profile.get_task(context.args.get("task_id"))
    if task is None:
        return context.logger.log_error("Task not found")

    assignees = context.args.get("assignee")

    for a in assignees:
        if a in task.assigned_to:
            task.assigned_to.remove(a)

    context.profile.save()
    context.logger.log_success(f"Updated task {task.name} [{task.id}]")
    log_task(context, task)
