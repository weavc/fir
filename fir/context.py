from tabulate import tabulate
from termcolor import colored
from fir.data.profile import Profile
from fir.data.settings import Settings
from fir.logger import Logger
from fir.types.dtos import TaskDto


class Context:
    profile: Profile
    settings: Settings
    args: tuple[str, dict]
    logger: Logger

    def __init__(self):
        pass

    def setup(self, args: dict, profile: Profile, settings: Settings):
        self.profile = profile
        self.settings = settings
        self.args = args
        self.logger = Logger(verbose=args.get("verbose"),
                             pretty=args.get("pretty"),
                             silent=args.get("silent"),
                             debug=args.get("debug"))

    def log_task_table_from_statuses(self, statuses: list):
        tasks = []
        for task in self.profile.data.tasks:
            if task.status in statuses:
                tasks.append(task)

        self.log_task_table(tasks)

    def sort_by_status_type(self, task: TaskDto):
        is_type = self.profile.check_status_type(task.status)
        if is_type == "todo":
            return 3000 + task.priority
        if is_type == "doing":
            return 2000 + task.priority
        if is_type == "done":
            return 1000 + task.priority

        return 4000 + task.priority

    def log_task_table(self, tasks: list[TaskDto], order: bool = True):

        table = []

        if order:
            tasks.sort(key=lambda x: self.sort_by_status_type(x))

        enabled = self.__enabled_columns()

        for task in tasks:
            status = self.__get_status_colour(task.status)

            values = [colored(task.id, 'light_grey'), task.name, status]
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

    def invalid_config_option(self):
        return self.logger.log_error(
            f"{self.args.get('config_name')} is not a valid option. Try 'fir config opts' for more information.")

    def link_profile(self, name: str, path: str):
        p = Profile(path)
        if p.data is None:
            return self.logger.log_error("Invalid profile")

        self.settings.data.profiles[name] = path
        self.settings.save()

    def __get_status_colour(self, status: str):
        is_type = self.profile.check_status_type(status)
        if is_type == "todo":
            status = colored(status, 'light_red')
        if is_type == "doing":
            status = colored(status, 'light_yellow')
        if is_type == "done":
            status = colored(status, 'light_green')

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
