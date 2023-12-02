from collections import defaultdict
import os
from tabulate import tabulate
from termcolor import colored

from fir.cmd.cmd_builder import CmdBuilder
from fir.context import Context
from fir.data.defaults import default_profile_struct
from fir.data.profile import Profile
from fir.types.dtos import LinkedProfilesDto


class ProfileHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = "profile"
    aliases = []


@ProfileHandlers.command("link")
@ProfileHandlers.add_positional("path")
@ProfileHandlers.add_positional("profile_name")
@ProfileHandlers.add_optional_flag("set", "--set")
def create(context: Context):
    name = context.args.get("profile_name")
    path = os.path.abspath(context.args.get("path"))
    p = Profile(path)
    if p.data is None:
        return context.logger.log_error("Invalid profile")

    context.settings.data.profiles[name] = path
    context.settings.save()
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


# @ProfileHandlers.command("create", aliases=["c"])
# @ProfileHandlers.add_positional("profile_name")
# @ProfileHandlers.add_optional("description", "--description", "-d")
# def create(context: Context):
#     context.data.add_profile(
#         context.args.get("profile_name"),
#         default_profile_struct(context.args.get("profile_name"), description=context.args.get("description")))

#     context.logger.log_success("Profile added")


# @ProfileHandlers.command("remove", aliases=["rm"])
# @ProfileHandlers.add_positional("profile_name")
# def remove(context: Context):
#     profile_name = context.args.get("profile_name")
#     profile = context.data.get_profile(profile_name)
#     if profile is None:
#         context.logger.log_error("Profile not found")

#     context.data.remove_profile(profile_name)
#     context.logger.log_success("Profile removed")


# @ProfileHandlers.command("list", aliases=["ls"])
# def ls(context: Context):
#     profiles = context.data.get_profiles()
#     table = []
#     for p in profiles:
#         profile = profiles.get(p)
#         table.append([profile.get("id"), p, profile.get("description")])

#     context.logger.log(tabulate(table,
#                                 headers=[f"{colored('Id', 'light_green', attrs=['bold'])}",
#                                          f"{colored('Profile', 'light_green', attrs=['bold'])}",
#                                          f"{colored('Description', 'light_green', attrs=['bold'])}"]))
