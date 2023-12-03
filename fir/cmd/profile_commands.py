import os
from collections import defaultdict
from tabulate import tabulate
from termcolor import colored
from slugify import slugify

from fir.builder import CmdBuilderDecorators, Cmd
from fir.config import DATA_DIR
from fir.context import Context
from fir.data.defaults import default_profile
from fir.data.profile import Profile
from fir.types.parameters import ParameterMap as pm


class ProfileHandlers(CmdBuilderDecorators):
    name = "profile"
    aliases = []
    cmds: dict[str, Cmd] = {}


@ProfileHandlers.command(Cmd("link", description="Link an existing fir profile file."))
@ProfileHandlers.add_positional(pm["profile_path"], pm["profile_name"])
@ProfileHandlers.add_optional_flag(pm["profile_set"])
def link(context: Context):
    name = context.args.get("profile_name")
    path = os.path.abspath(context.args.get("profile_path"))

    context.link_profile(name, path)

    context.logger.log_success(f"Profile {name} added")
    if context.args.get("profile_set"):
        set(context)


@ProfileHandlers.command(Cmd("set",
                         aliases=["set"],
                         description="Set scope to target profile. See available profiles using 'fir profile ls'."))
@ProfileHandlers.add_positional(pm["profile_name"])
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


@ProfileHandlers.command(Cmd("create", aliases=["c", "new"], description="Create a new fir profile."))
@ProfileHandlers.add_positional(pm["profile_name"])
@ProfileHandlers.add_optional(pm["profile_path"], pm["description"])
@ProfileHandlers.add_optional_flag(pm["profile_set"], pm["force"])
def create(context: Context):
    name = context.args.get("profile_name")
    desc = ""
    if context.args.get("description"):
        desc = context.args.get("description")

    path = os.path.abspath(os.path.join(DATA_DIR, f"{slugify(name)}.toml"))
    if context.args.get("path"):
        dir_path = os.path.abspath(context.args.get("profile_path"))
        if os.path.isdir(dir_path):
            path = os.path.join(dir_path, f"{slugify(name)}.toml")
        else:
            path = dir_path

    if os.path.exists(path) and not context.args.get("force"):
        return context.logger.log_error("File already exists")

    profile = Profile(path=path, read=False)
    profile.data = default_profile(name, desc)
    profile.save()

    context.link_profile(context, name, path)
    context.logger.log_success(f"Profile {name} added")
    if context.args.get("profile_set"):
        set(context)


@ProfileHandlers.command(Cmd("remove", aliases=["rm"], description="Remove fir profile. Does not remove the file."))
@ProfileHandlers.add_positional(pm["profile_name"])
def remove(context: Context):
    profile_name = context.args.get("profile_name")
    profile = context.settings.data.profiles.get(profile_name, None)
    if profile is None:
        context.logger.log_error("Profile not found")

    context.settings.data.profiles.pop(profile_name)
    context.settings.save()
    context.logger.log_success("Profile removed")


@ProfileHandlers.command(Cmd("list", aliases=["ls"], description="List linked profiles."))
def ls(context: Context):
    table = []
    for key in context.settings.data.profiles.keys():
        table.append([key, context.settings.data.profiles[key]])

    context.logger.log(tabulate(table,
                                headers=[f"{colored('Id', 'light_blue', attrs=['bold'])}",
                                         f"{colored('Path', 'light_blue', attrs=['bold'])}"]))
