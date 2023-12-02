from tabulate import tabulate
from termcolor import colored
from fir.context import Context
from fir.helpers.dates import str_to_date_string
from fir.types.dtos import TaskDto


def log_task_table_from_statuses(context: Context, statuses: list):
    tasks = []
    for task in context.profile.data.tasks:
        if task.status in statuses:
            tasks.append(task)

    log_task_table(context, tasks)


def log_task_table(context: Context, tasks: list[TaskDto]):
    table = []
    for task in tasks:
        status = task.status
        is_type = context.profile.check_status_type(status)
        if is_type == "todo":
            status = colored(task.status, 'light_red')
        if is_type == "doing":
            status = colored(task.status, 'light_yellow')
        if is_type == "done":
            status = colored(task.status, 'light_green')

        table.append([
            colored(task.id, 'light_grey'),
            task.name,
            status,
            task.due,
            ', '.join(task.tags)])

    context.logger.log(tabulate(table,
                                headers=[f"{colored('Id', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Task', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Status', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Due', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Tags', 'light_blue', attrs=['bold'])}"
                                         ]))


def log_task(context: Context, task: TaskDto):
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


def parse_date_from_arg(context: Context, date: str):
    dt = ""
    if date:
        try:
            dt = str_to_date_string(date)
        except ValueError:
            return context.logger.log_error(f"Unable to parse date from due date")

    return dt
