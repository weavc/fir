import os

from fir.config import DATA_DIR
from fir.data.defaults import default_profile
from fir.utils import str2bool
from fir.types.config_options import ConfigOptions, ConfigOptionsMap
from fir.types.dtos import StatusDto, TaskDto, ProfileDto
from fir.utils.files import read_toml_file, write_toml_file


class Profile:
    path: str
    data: ProfileDto
    has_read: bool = False

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

    def read(self):
        return self.__read()

    def get_task(self, id: str) -> (TaskDto | None, str):
        vals = [x for x in self.data.tasks if x.id.startswith(id)]
        if len(vals) > 1:
            return None, "Conflicting tasks found, use full id value"            
        n = next((v for v in vals), None)
        if n is None:
            return None, "Task not found"
        return n, None

    def set_status(self, task: TaskDto, status: str) -> bool:
        if status not in self.get_status_names():
            return False

        task.status = status
        return True

    def try_get_config_value(self, key: ConfigOptions):
        value = self.data.config.get(key, None)
        if value is None:
            value = ConfigOptionsMap.get(key).default

        return value

    def try_get_config_value_int(self, key: ConfigOptions):
        return int(self.try_get_config_value(key))

    def try_get_config_value_bool(self, key: ConfigOptions):
        return str2bool(self.try_get_config_value(key))

    def try_get_config_value_list(self, key: ConfigOptions):
        value = self.try_get_config_value(key)
        if value is None:
            return None
        return [x.strip() for x in value.split(',')]

    def get_status_by_name(self, name: str) -> StatusDto | None:
        for s in self.data.statuses:
            if s.name == name:
                return s
        return None

    def get_status_names(self) -> list[str]:
        return [s.name for s in self.data.statuses]

    def __read(self):
        self.__check_dir()
        d = read_toml_file(self.path)
        self.data = ProfileDto.Schema().load(d)
        self.has_read = True

    def __save(self):
        self.__check_dir()
        s = ProfileDto.Schema().dump(self.data)
        write_toml_file(self.path, s)

    def __check_dir(self):
        if not os.path.isdir(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
            except PermissionError:
                print(
                    f'ERROR!\nNo permission to write to "{DATA_DIR}" directory!')
                raise SystemExit(1)
