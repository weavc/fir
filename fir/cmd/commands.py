from tabulate import tabulate

from fir.cmd.handlers import Handlers
from fir.context import Context
from fir.helpers import print_err

@Handlers.command("add", aliases=["a"])
@Handlers.add_positional("profile_name")
@Handlers.add_optional("description", "--description", "-d")
def add(context: Context):
    context.data.add_profile(context.args.get("profile_name"))
    edit(context)
    
@Handlers.command("remove", aliases=["rm"])
@Handlers.add_positional("profile_name")
def remove(context: Context):
    context.data.remove_profile(context.args.get("profile_name"))
    
@Handlers.command("list", aliases=["ls"])
def ls(context: Context):
    profiles = context.data.get_profiles()
    table = []
    for p in profiles:
        profile = profiles.get(p)
        table.append([p, profile.get("description")])

    print(tabulate(table, headers=["profile", "description"]))

@Handlers.command("edit", aliases=["e"])
@Handlers.add_positional("profile_name")
@Handlers.add_optional("description", "--description", "-d")
def edit(context: Context):
    profile_name = context.args.get("profile_name")
    profile = context.data.get_profile(profile_name)
    if profile is None:
        print_err("Profile not found")

    profile.update({"description": context.args.get("description")})
    context.data.update_profile(profile_name, profile)

    print(f"Updated profile {profile_name}")