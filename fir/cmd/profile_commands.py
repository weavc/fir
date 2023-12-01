from collections import defaultdict
from tabulate import tabulate
from termcolor import colored

from fir.cmd.cmd_builder import CmdBuilder
from fir.context import Context
from fir.data.defaults import default_profile_struct

class ProfileHandlers(CmdBuilder):
    commands = defaultdict(dict)
    name = "profile"
    aliases = []

@ProfileHandlers.command("create", aliases=["c"])
@ProfileHandlers.add_positional("profile_name")
@ProfileHandlers.add_optional("description", "--description", "-d")
def create(context: Context):
    context.data.add_profile(
        context.args.get("profile_name"), 
        default_profile_struct(context.args.get("profile_name"), description=context.args.get("description")))

    context.logger.log_success("Profile added")

@ProfileHandlers.command("modify", aliases=["mod", "m"])
@ProfileHandlers.add_positional("profile_name")
@ProfileHandlers.add_optional("description", "--description", "-d")
def modify(context: Context):
    profile_name = context.args.get("profile_name")
    update_profile = context.data.get_profile(profile_name)
    if update_profile is None:
        context.logger.log_error("Profile not found")

    update_profile.update({"description": context.args.get("description")})
    context.data.update_profile(profile_name, update_profile)

    context.logger.log_success(f"Updated profile {profile_name}")

@ProfileHandlers.command("remove", aliases=["rm"])
@ProfileHandlers.add_positional("profile_name")
def remove(context: Context):
    profile_name = context.args.get("profile_name")
    profile = context.data.get_profile(profile_name)
    if profile is None:
        context.logger.log_error("Profile not found")

    context.data.remove_profile(profile_name)
    context.logger.log_success("Profile removed")
    
@ProfileHandlers.command("list", aliases=["ls"])
def ls(context: Context):
    profiles = context.data.get_profiles()
    table = []
    for p in profiles:
        profile = profiles.get(p)
        table.append([profile.get("id"), p, profile.get("description")])

    context.logger.log(tabulate(table, 
        headers=[f"{colored('Id', 'light_green', attrs=['bold'])}", 
                 f"{colored('Profile', 'light_green', attrs=['bold'])}", 
                 f"{colored('Description', 'light_green', attrs=['bold'])}"]))
    
@ProfileHandlers.command("set", aliases=["set"])
@ProfileHandlers.add_positional("profile_name")
def set(context: Context):
    new_profile = context.data.get_profile(context.args.get("profile_name"))
    if new_profile is None:
        context.logger.log_error("Profile not found")

    context.data.scope = context.args.get("profile_name")
    context.logger.log_success(f"Set profile to {context.args.get('profile_name')}")