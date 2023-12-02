import os

from fir.config import DATA_DIR
from fir.model.schemas import ProfileDto, ProfileSchema
from fir.helpers import read_toml_file, write_toml_file


class Profile:
    path = os.path.join(DATA_DIR, "profiles.toml")
    data: ProfileDto

    def __init__(self):
        self.__read()

    def save(self):
        return self.__save()

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
