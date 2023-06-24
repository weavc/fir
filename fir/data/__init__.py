import os

from fir.cfg.env_dev import DATA_DIR
from fir.helpers import write_json_file, read_json_file

class Data:

    profiles_path = os.path.join(DATA_DIR, "profiles.json")
    data = {
        "profiles": {
        }
    }

    def __init__(self):
        self.read()

    def get_profiles(self) -> dict:
        return self.data.get("profiles")

    def get_profile(self, name: str) -> dict:
        self.get_profiles()
        return self.get_profiles().get(name)

    def add_profile(self, name: str) -> dict:
        profile = self.get_profile(name)
        if profile is None:
            profile = self.__default_profile_struct()
            self.data.get("profiles").update({name: profile})
        self.save()
        return profile
    
    def update_profile(self, name: str, profile: dict) -> dict:
        profile = self.get_profile(name)
        if profile is None:
            return None
        self.data.get("profiles").update({name: profile})
        self.save()
        return profile

    def remove_profile(self, name: str) -> dict:
        profile = self.get_profile(name)
        if profile is not None:
            self.data.get("profiles").pop(name)

        self.save()
        return profile
    
    def read(self):
        self.__check_dir()
        if not os.path.exists(self.profiles_path):
            self.save()
        self.data = read_json_file(self.profiles_path)


    def save(self):
        self.__check_dir()
        write_json_file(self.profiles_path, self.data)
    
    
    def __check_dir(self):
        if not os.path.isdir(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
            except PermissionError:
                print(f'ERROR!\nNo permission to write to "{DATA_DIR}" directory!')
                raise SystemExit(1)


    def __default_profile_struct(self):
        return {
                "description": "",
                "tasks": [],
                "config": {}
            }

    def __default_task_struct(self, name: str):
        return { 
                "name": name,
                "tags": [],
                "status": ""
            }
    
# todo write a backup file before saving