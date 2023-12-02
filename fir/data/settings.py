import os

from fir.config import DATA_DIR
from fir.data.defaults import default_settings
from fir.types.dtos import SettingsDto
from fir.types.schemas import SettingsSchema
from fir.helpers.files import read_toml_file, write_toml_file


class Settings:
    path = os.path.join(DATA_DIR, "settings.v1.toml")
    data: SettingsDto

    def __init__(self):
        self.__read()

    def get_profile(self, name: str) -> (str, str):
        profile = self.data.profiles.get(name, None)
        if profile is None:
            return None, None

        return self.data.scope, profile

    def get_scoped_profile(self) -> (str, str):
        return self.get_profile(self.data.scope)

    def save(self):
        return self.__save()

    def __read(self):
        self.__check_dir()
        
        if not os.path.exists(self.path):
            self.data = default_settings()
            self.save()

        d = read_toml_file(self.path)
        self.data = SettingsSchema().load(d)

    def __save(self):
        self.__check_dir()
        s = SettingsSchema().dump(self.data)
        write_toml_file(self.path, s)

    def __check_dir(self):
        if not os.path.isdir(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
            except PermissionError:
                print(f'ERROR!\nNo permission to write to "{DATA_DIR}" directory!')
                raise SystemExit(1)
