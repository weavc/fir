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
        return 3000 + task.priority
    if is_type == "doing":
        return 2000 + task.priority
    if is_type == "done":
        return 1000 + task.priority

    return 4000 + task.priority


def log_task_table(context: Context, tasks: list[TaskDto], order: bool = True):
    # Might want to tidy the if statements in here at some point. I think
    # theres probably a way to do this automatically when the settings/fields are added
    
    table = []

    if order:
        tasks.sort(key=lambda x: sort_by_status_type(context, x))

    enable_tags = context.profile.try_get_config_value_bool("enable.column.tags")
    enable_due = context.profile.try_get_config_value_bool("enable.column.due")
    enable_description = context.profile.try_get_config_value_bool("enable.column.description")
    enable_link = context.profile.try_get_config_value_bool("enable.column.link")
    enable_assigned = context.profile.try_get_config_value_bool("enable.column.assigned")
    enable_priority = context.profile.try_get_config_value_bool("enable.column.priority")

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
        if enable_description:
            values.append(task.description)
        if enable_link:
            values.append(task.link)
        if enable_due:
            values.append(task.due)
        if enable_priority:
            values.append(task.priority)
        if enable_assigned:
            values.append(', '.join(task.assigned_to))
        if enable_tags:
            values.append(', '.join(task.tags))
        
        table.append(values)

    headers = [f"{colored('Id', 'light_blue', attrs=['bold'])}",
               f"{colored('Task', 'light_blue', attrs=['bold'])}",
               f"{colored('Status', 'light_blue', attrs=['bold'])}"]

    if enable_description:
        headers.append(f"{colored('Description', 'light_blue', attrs=['bold'])}")
    if enable_link:
        headers.append(f"{colored('Link', 'light_blue', attrs=['bold'])}")
    if enable_due:
        headers.append(f"{colored('Due Date', 'light_blue', attrs=['bold'])}")
    if enable_priority:
        headers.append(f"{colored('Priority', 'light_blue', attrs=['bold'])}")
    if enable_assigned:
        headers.append(f"{colored('Assigned To', 'light_blue', attrs=['bold'])}")
    if enable_tags:
        headers.append(f"{colored('Tags', 'light_blue', attrs=['bold'])}")

    context.logger.log(tabulate(table, headers=headers))


def log_task(context: Context, task: TaskDto):
    context.logger.log(f"{colored('Id', 'light_blue', attrs=['bold'])}: {task.id}")
    context.logger.log(f"{colored('Name', 'light_blue', attrs=['bold'])}: {task.name}")
    context.logger.log(f"{colored('Status', 'light_blue', attrs=['bold'])}: {task.status}")
    
    if task.description:
        context.logger.log(f"{colored('Description', 'light_blue', attrs=['bold'])}: {task.description}")
    if task.due:
        context.logger.log(f"{colored('Due Date', 'light_blue', attrs=['bold'])}: {task.due}")
    if task.link:
        context.logger.log(f"{colored('Link', 'light_blue', attrs=['bold'])}: {task.link}")
    if task.assigned_to:
        context.logger.log(f"{colored('Assigned To', 'light_blue', attrs=['bold'])}: {', '.join(task.assigned_to)}")
    if task.tags:
        context.logger.log(f"{colored('Tags', 'light_blue', attrs=['bold'])}: {', '.join(task.tags)}")
    if task.priority:
        context.logger.log(f"{colored('Priority', 'light_blue', attrs=['bold'])}: {task.priority}")
    

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
