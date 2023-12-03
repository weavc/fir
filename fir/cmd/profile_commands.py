import os
from collections import defaultdict
from tabulate import tabulate
from termcolor import colored
from slugify import slugify

from fir.cmd.cmd_builder import CmdBuilder
from fir.config import DATA_DIR
from fir.context import Context
from fir.data.defaults import default_profile
from fir.data.profile import Profile
from fir.helpers.commands import link_profile


class ProfileHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = "profile"
    aliases = []


@ProfileHandlers.command("link")
@ProfileHandlers.add_positional("path")
@ProfileHandlers.add_positional("profile_name")
@ProfileHandlers.add_optional_flag("set", "--set")
def link(context: Context):
    name = context.args.get("profile_name")
    path = os.path.abspath(context.args.get("path"))

    link_profile(context, name, path)

    context.logger.log_success(f"Profile {name} added")
    if context.args.get("set"):
        set(context)


@ProfileHandlers.command("set", aliases=["set"])
@ProfileHandlers.add_positional("profile_name")
def set(context: Context):
    name = context.args.get("profile_name")
    path = context.settings.data.profiles.get(name)
    if path is None:
        return context.logger.log_error("Invalid profile")

    p = Profile(path)
    if p.data is None:
        return context.logger.log_error("Invalid profile")

    context.settings.data.scope = name
    context.settings.save()
    context.logger.log_success(f"Set profile to {name}")


@ProfileHandlers.command("create", aliases=["c", "new"])
@ProfileHandlers.add_positional("profile_name")
@ProfileHandlers.add_optional("description", "--description", "-d")
@ProfileHandlers.add_optional("path", "--path")
@ProfileHandlers.add_optional_flag("set", "--set")
@ProfileHandlers.add_optional_flag("force", "--force")
def create(context: Context):
    name = context.args.get("profile_name")
    desc = ""
    if context.args.get("description"):
        desc = context.args.get("description")

    path = os.path.abspath(os.path.join(DATA_DIR, f"{slugify(name)}.toml"))
    if context.args.get("path"):
        dir_path = os.path.abspath(context.args.get("path"))
        if os.path.isdir(dir_path):
            path = os.path.join(dir_path, f"{slugify(name)}.toml")
        else:
            path = dir_path

    if os.path.exists(path) and not context.args.get("force"):
        return context.logger.log_error("File already exists")

    profile = Profile(path=path, read=False)
    profile.data = default_profile(name, desc)
    profile.save()

    link_profile(context, name, path)
    context.logger.log_success(f"Profile {name} added")
    if context.args.get("set"):
        set(context)


@ProfileHandlers.command("remove", aliases=["rm"])
@ProfileHandlers.add_positional("profile_name")
def remove(context: Context):
    profile_name = context.args.get("profile_name")
    profile = context.settings.data.profiles.get(profile_name, None)
    if profile is None:
        context.logger.log_error("Profile not found")

    context.settings.data.profiles.pop(profile_name)
    context.settings.save()
    context.logger.log_success("Profile removed")


@ProfileHandlers.command("list", aliases=["ls"])
def ls(context: Context):
    table = []
    for key in context.settings.data.profiles.keys():
        table.append([key, context.settings.data.profiles[key]])

    context.logger.log(tabulate(table,
                                headers=[f"{colored('Id', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Path', 'light_blue', attrs=['bold'])}"]))
