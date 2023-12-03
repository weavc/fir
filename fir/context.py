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
        # Might want to tidy the if statements in here at some point. I think
        # theres probably a way to do this automatically when the settings/fields are added

        table = []

        if order:
            tasks.sort(key=lambda x: self.sort_by_status_type(x))

        enable_tags = self.profile.try_get_config_value_bool("enable.column.tags")
        enable_due = self.profile.try_get_config_value_bool("enable.column.due")
        enable_description = self.profile.try_get_config_value_bool("enable.column.description")
        enable_link = self.profile.try_get_config_value_bool("enable.column.link")
        enable_assigned = self.profile.try_get_config_value_bool("enable.column.assigned")
        enable_priority = self.profile.try_get_config_value_bool("enable.column.priority")

        for task in tasks:
            status = task.status
            is_type = self.profile.check_status_type(status)
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
