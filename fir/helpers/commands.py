from tabulate import tabulate
from termcolor import colored
from fir.context import Context
from fir.data.profile import Profile
from fir.helpers.dates import str_to_date_string
from fir.types.dtos import TaskDto


def log_task_table_from_statuses(context: Context, statuses: list):
    tasks = []
    for task in context.profile.data.tasks:
        if task.status in statuses:
            tasks.append(task)

    log_task_table(context, tasks)


def sort_by_status_type(context: Context, task: TaskDto):
    is_type = context.profile.check_status_type(task.status)
    if is_type == "todo":
        return 300
    if is_type == "doing":
        return 200
    if is_type == "done":
        return 100

    return 400


def log_task_table(context: Context, tasks: list[TaskDto], order: bool = True):
    table = []

    if order:
        tasks.sort(key=lambda x: sort_by_status_type(context, x))

    enable_tags = context.profile.try_get_config_value_bool("enable.ls.column.tags")
    enable_due = context.profile.try_get_config_value_bool("enable.ls.column.due")

    for task in tasks:
        status = task.status
        is_type = context.profile.check_status_type(status)
        if is_type == "todo":
            status = colored(task.status, 'light_red')
        if is_type == "doing":
            status = colored(task.status, 'light_yellow')
        if is_type == "done":
            status = colored(task.status, 'light_green')

        values = [colored(task.id, 'light_grey'), task.name, status]
        if enable_due:
            values.append(task.due)
        if enable_tags:
            values.append(', '.join(task.tags))
        
        table.append(values)
        
    headers = [f"{colored('Id', 'light_blue', attrs=['bold'])}",
            f"{colored('Task', 'light_blue', attrs=['bold'])}",
            f"{colored('Status', 'light_blue', attrs=['bold'])}"]
    
    if enable_due:
        headers.append(f"{colored('Due Date', 'light_blue', attrs=['bold'])}")

    if enable_tags:
        headers.append(f"{colored('Tags', 'light_blue', attrs=['bold'])}")

    context.logger.log(tabulate(table, headers=headers))

def log_task(context: Context, task: TaskDto):
    context.logger.log(f"{colored('Id', 'light_blue', attrs=['bold'])}: {task.id}")
    context.logger.log(f"{colored('Name', 'light_blue', attrs=['bold'])}: {task.name}")
    context.logger.log(f"{colored('Status', 'light_blue', attrs=['bold'])}: {task.status}")
    
    if task.due:
        context.logger.log(f"{colored('Due', 'light_blue', attrs=['bold'])}: {task.due}")
    if task.tags:
        context.logger.log(f"{colored('Tags', 'light_blue', attrs=['bold'])}: {', '.join(task.tags)}")


def parse_date_from_arg(context: Context, date: str):
    dt = ""
    if date:
        try:
            dt = str_to_date_string(date)
        except ValueError:
            return context.logger.log_error(f"Unable to parse date from due date")

    return dt


def invalid_config_option(context: Context):
    return context.logger.log_error(f"{context.args.get('config_name')} is not a valid option. Try 'fir config opts' for more information.")


def link_profile(context: Context, name: str, path: str):
    p = Profile(path)
    if p.data is None:
        return context.logger.log_error("Invalid profile")

    context.settings.data.profiles[name] = path
    context.settings.save()