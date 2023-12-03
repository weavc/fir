import os
from tabulate import tabulate
from termcolor import colored
from slugify import slugify

from fir.builder import CmdBuilder, Cmd
from fir.config import DATA_DIR
from fir.context import Context
from fir.data.defaults import default_profile
from fir.data.profile import Profile
from fir.types.parameters import ParameterMap as pm


class ProfileHandlers(CmdBuilder):
    name = "profile"
    aliases = []
    cmds: dict[str, Cmd] = {}

    context: Context

    def __init__(self, context: Context):
        self.context = context
        self.register_commands(*[t for t in self.map()])

    def map(self) -> list[Cmd]:
        return [
            Cmd("link",
                description="Link an existing fir profile file.",
                args=[pm["profile_name"], pm["profile_path"]],
                optionals=[pm["profile_set"]],
                func=self.link),
            Cmd("set",
                aliases=["set"],
                description="Set scope to target profile. See available profiles using 'fir profile ls'.",
                args=[pm["profile_name"]],
                func=self.set),
            Cmd("create",
                aliases=["c", "new"],
                description="Create a new fir profile.",
                args=[pm["profile_name"]],
                optionals=[pm["description"], pm["profile_path"]],
                flags=[pm["profile_set"], pm["force"]],
                func=self.create),
            Cmd("remove",
                aliases=["rm"],
                description="Remove fir profile. Does not remove the file.",
                args=[pm["profile_name"]],
                func=self.remove),
            Cmd("list",
                aliases=["ls"],
                description="List linked profiles.",
                func=self.ls)
        ]

    def link(self):
        name = self.context.args.get("profile_name")
        path = os.path.abspath(self.context.args.get("profile_path"))

        self.context.link_profile(name, path)

        self.context.logger.log_success(f"Profile {name} added")
        if self.context.args.get("profile_set"):
            self.set()

    def set(self):
        name = self.context.args.get("profile_name")
        path = self.context.settings.data.profiles.get(name)
        if path is None:
            return self.context.logger.log_error("Invalid profile")

        p = Profile(path)
        if p.data is None:
            return self.context.logger.log_error("Invalid profile")

        self.context.settings.data.scope = name
        self.context.settings.save()
        self.context.logger.log_success(f"Set profile to {name}")

    def create(self):
        name = self.context.args.get("profile_name")
        desc = ""
        if self.context.args.get("description"):
            desc = self.context.args.get("description")

        path = os.path.abspath(os.path.join(DATA_DIR, f"{slugify(name)}.toml"))
        if self.context.args.get("profile_path"):
            dir_path = os.path.abspath(self.context.args.get("profile_path"))
            if os.path.isdir(dir_path):
                path = os.path.join(dir_path, f"{slugify(name)}.toml")
            else:
                path = dir_path

        if os.path.exists(path) and not self.context.args.get("force"):
            return self.context.logger.log_error("File already exists")

        profile = Profile(path=path, read=False)
        profile.data = default_profile(name, desc)
        profile.save()

        self.context.link_profile(name, path)
        self.context.logger.log_success(f"Profile {name} added")
        if self.context.args.get("profile_set"):
            self.set()

    def remove(self):
        profile_name = self.context.args.get("profile_name")
        profile = self.context.settings.data.profiles.get(profile_name, None)
        if profile is None:
            self.context.logger.log_error("Profile not found")

        self.context.settings.data.profiles.pop(profile_name)
        self.context.settings.save()
        self.context.logger.log_success("Profile removed")

    def ls(self):
        table = []
        for key in self.context.settings.data.profiles.keys():
            table.append([key, self.context.settings.data.profiles[key]])

        self.context.logger.log(tabulate(table,
                                    headers=[f"{colored('Id', 'light_blue', attrs=['bold'])}",
                                             f"{colored('Path', 'light_blue', attrs=['bold'])}"]))
