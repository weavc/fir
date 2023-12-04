import os

from fir.config import DATA_DIR
from fir.data.defaults import default_profile
from fir.helpers import str2bool
from fir.types import ConfigOptions, ConfigOptionsMap, StatusTypes
from fir.types.dtos import TaskDto
from fir.types.schemas import ProfileDto, ProfileSchema
from fir.helpers.files import read_toml_file, write_toml_file


class Profile:
    path: str
    data: ProfileDto

    def __init__(self, path: str = None, read: bool = True):
        self.path = path
        if self.path is None:
            self.path = os.path.join(DATA_DIR, "default.toml")
            if not os.path.exists(self.path):
                self.data = default_profile("default")
                self.save()

        if read:
            self.__read()

    def save(self):
        return self.__save()

    def get_task(self, id: str) -> TaskDto | None:
        return next((x for x in self.data.tasks if x.id.startswith(id)), None)

    def set_status(self, task: TaskDto, status: str) -> bool:
        if status not in self.get_valid_statuses():
            return False

        task.status = status
        return True

    def try_get_config_value(self, key: ConfigOptions):
        value = self.data.config.get(key, None)
        if value is None:
            value = ConfigOptionsMap.get(key).default

        return value

    def try_get_config_value_bool(self, key: ConfigOptions):
        return str2bool(self.try_get_config_value(key))

    def try_get_config_value_list(self, key: ConfigOptions):
        value = self.try_get_config_value(key)
        if value is None:
            return None
        return [x.strip() for x in value.split(',')]

    def get_valid_statuses(self):
        statuses = []
        statuses.extend(self.get_todo_statuses())
        statuses.extend(self.get_doing_statuses())
        statuses.extend(self.get_done_statuses())
        return statuses

    def get_todo_statuses(self):
        return self.try_get_config_value_list("status.todo")

    def get_doing_statuses(self):
        return self.try_get_config_value_list("status.doing")

    def get_done_statuses(self):
        return self.try_get_config_value_list("status.done")

    def check_status_type(self, status: str) -> StatusTypes | None:
        if status in self.get_todo_statuses():
            return "todo"
        if status in self.get_doing_statuses():
            return "doing"
        if status in self.get_done_statuses():
            return "done"

        return None

    def __read(self):
        self.__check_dir()
        d = read_toml_file(self.path)
        self.data = ProfileSchema().load(d)

    def __save(self):
        self.__check_dir()
        s = ProfileSchema().dump(self.data)
        write_toml_file(self.path, s)

    def __check_dir(self):
        if not os.path.isdir(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
            except PermissionError:
                print(
                    f'ERROR!\nNo permission to write to "{DATA_DIR}" directory!')
                raise SystemExit(1)
