
from logging import Logger
from tabulate import tabulate

from termcolor import colored
from fir.data.profile import Profile
from fir.types.dtos import TaskDto
from fir.utils import truncate


class ProfileLoggingExtensions:
    logger: Logger

    def __init__(self, logger: Logger, profile: Profile):
        self.profile = profile
        self.logger = logger

    
    def log_task_table(self, tasks: list[TaskDto], order: bool = True):
        table = []
        if order:
            tasks.sort(key=lambda x: self.sort_by_status_type(x))

        enabled = self.__enabled_columns()

        for task in tasks:
            status = self.__get_status_colour(task.status)

            values = [colored(task.id, 'light_grey'),
                      truncate(task.name, self.profile.try_get_config_value_int("name.truncate")),
                      status]
            if enabled.get("description"):
                values.append(task.description)
            if enabled.get("link"):
                values.append(task.link)
            if enabled.get("due"):
                values.append(task.due)
            if enabled.get("priority"):
                values.append(task.priority)
            if enabled.get("assigned"):
                values.append(', '.join(task.assigned_to))
            if enabled.get("tags"):
                values.append(', '.join(task.tags))

            table.append(values)

        headers = self.__get_headers(enabled)

        self.logger.log(tabulate(table, headers=headers))

    def log_task(self, task: TaskDto):
        self.logger.log(f"{colored('Id', 'light_blue', attrs=['bold'])}: {task.id}")
        self.logger.log(f"{colored('Name', 'light_blue', attrs=['bold'])}: {task.name}")
        self.logger.log(f"{colored('Status', 'light_blue', attrs=['bold'])}: {task.status}")

        if task.description:
            self.logger.log(f"{colored('Description', 'light_blue', attrs=['bold'])}: {task.description}")
        if task.due:
            self.logger.log(f"{colored('Due Date', 'light_blue', attrs=['bold'])}: {task.due}")
        if task.link:
            self.logger.log(f"{colored('Link', 'light_blue', attrs=['bold'])}: {task.link}")
        if task.assigned_to:
            self.logger.log(f"{colored('Assigned To', 'light_blue', attrs=['bold'])}: {', '.join(task.assigned_to)}")
        if task.tags:
            self.logger.log(f"{colored('Tags', 'light_blue', attrs=['bold'])}: {', '.join(task.tags)}")
        if task.priority:
            self.logger.log(f"{colored('Priority', 'light_blue', attrs=['bold'])}: {task.priority}")

    def log_task_table_from_statuses(self, statuses: list):
        tasks = []
        for task in self.profile.data.tasks:
            if task.status in statuses:
                tasks.append(task)

        self.log_task_table(tasks)

    def sort_by_status_type(self, task: TaskDto):
        p = 1000
        status = self.profile.get_status_by_name(task.status)
        if status is not None:
            p = status.order

        return p

    def __get_status_colour(self, status: str):
        s = self.profile.get_status_by_name(status)
        color = None
        if s is not None:
            color = s.color

        if color is not None:
            return colored(status, color)

        return status

    def __get_headers(self, enabled: dict[str, bool]):
        headers = [
            f"{colored('Id', 'light_blue', attrs=['bold'])}",
            f"{colored('Task', 'light_blue', attrs=['bold'])}",
            f"{colored('Status', 'light_blue', attrs=['bold'])}"]

        if enabled.get("description"):
            headers.append(f"{colored('Description', 'light_blue', attrs=['bold'])}")
        if enabled.get("link"):
            headers.append(f"{colored('Link', 'light_blue', attrs=['bold'])}")
        if enabled.get("due"):
            headers.append(f"{colored('Due Date', 'light_blue', attrs=['bold'])}")
        if enabled.get("priority"):
            headers.append(f"{colored('Priority', 'light_blue', attrs=['bold'])}")
        if enabled.get("assigned"):
            headers.append(f"{colored('Assigned To', 'light_blue', attrs=['bold'])}")
        if enabled.get("tags"):
            headers.append(f"{colored('Tags', 'light_blue', attrs=['bold'])}")

        return headers

    def __enabled_columns(self):
        return {
            "tags": self.profile.try_get_config_value_bool("enable.column.tags"),
            "due": self.profile.try_get_config_value_bool("enable.column.due"),
            "description": self.profile.try_get_config_value_bool("enable.column.description"),
            "link": self.profile.try_get_config_value_bool("enable.column.link"),
            "assigned": self.profile.try_get_config_value_bool("enable.column.assigned"),
            "priority": self.profile.try_get_config_value_bool("enable.column.priority"),
        }