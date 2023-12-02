import os

from fir.config import DATA_DIR
from fir.types.dtos import SettingsDto
from fir.types.schemas import SettingsSchema
from fir.helpers.files import read_toml_file, write_toml_file


class Settings:
    path = os.path.join(DATA_DIR, "settings.toml")
    data: SettingsDto

    def __init__(self):
        self.__read()

    def save(self):
        return self.__save()

    def __read(self):
        self.__check_dir()
        d = read_toml_file(self.path)
        self.data = SettingsSchema().load(d)

    def __save(self):
        self.__check_dir()
        s = SettingsSchema().dump(self.profile)
        write_toml_file(self.profiles_path, s)

    def __check_dir(self):
        if not os.path.isdir(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
            except PermissionError:
                print(f'ERROR!\nNo permission to write to "{DATA_DIR}" directory!')
                raise SystemExit(1)
