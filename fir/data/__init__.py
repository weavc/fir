from collections import defaultdict
import datetime
import os

from fir.config import DATA_DIR
from fir.data.defaults import default_profile_struct, default_task_struct
from fir.helpers.files import write_toml_file, read_toml_file


class Data:

    profiles_path = os.path.join(DATA_DIR, "profiles.toml")
    __data: dict = defaultdict(profiles={
        "default": default_profile_struct(
            name="default",
            description="Default profile",
            tasks=[default_task_struct("Example task", tags=["example"], status="TODO")])
    }, scope="default")

    def __init__(self):
        self.__read()

    def get_data(self):
        return self.__data

    @property
    def scope(self) -> str:
        return self.__data.get("scope")

    @scope.setter
    def scope(self, value: str):
        self.__data["scope"] = value
        self.__save()

    def get_profiles(self) -> dict:
        return self.__data.get("profiles")

    def get_profile(self, name: str) -> dict:
        self.get_profiles()
        return self.get_profiles().get(name)

    def add_profile(self, name: str, profile: dict) -> dict:
        exists = self.get_profile(name)
        if exists is None:
            self.__data.get("profiles").update({name: profile})
        self.__save()
        return profile

    def update_profile(self, name: str, profile: dict) -> dict:
        profile = self.get_profile(name)
        if profile is None:
            return None

        self.__data.get("profiles").update({name: profile})
        self.__save()
        return profile

    def remove_profile(self, name: str) -> dict:
        profile = self.get_profile(name)
        if profile is not None:
            self.__data.get("profiles").pop(name)

        self.__save()
        return profile

    def __read(self):
        self.__check_dir()
        if not os.path.exists(self.profiles_path):
            self.__save()
        self.__data = read_toml_file(self.profiles_path)

    def __save(self):
        self.__check_dir()
        write_toml_file(self.profiles_path, self.__data)

    def __check_dir(self):
        if not os.path.isdir(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
            except PermissionError:
                print(f'ERROR!\nNo permission to write to "{DATA_DIR}" directory!')
                raise SystemExit(1)
