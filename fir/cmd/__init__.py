import argparse
from fir.cmd.handlers import Handlers, ProfileHandlers
from fir.context import Context
from fir.data import Data
from fir.cmd.commands import *


def setup_argparser(data: Data):
    parser = argparse.ArgumentParser(description="Fir, command line task tracking")
    parser.add_argument("--verbose", "-v", action="store_true", dest="verbose", help="Prints more information", default=False)

    sub = parser.add_subparsers(dest="command", metavar="action")
    for profile in data.get_profiles():
        p = sub.add_parser(profile)
        sub_p = p.add_subparsers(dest="profile_command", metavar="action")
        for c in ProfileHandlers.commands:
            c_parser = sub_p.add_parser(ProfileHandlers.commands.get(c).get("name"), aliases=ProfileHandlers.commands.get(c).get("aliases"))
            setup_handlers(c, ProfileHandlers.commands, c_parser)

    for c in Handlers.commands:
        c_parser = sub.add_parser(Handlers.commands.get(c).get("name"), aliases=Handlers.commands.get(c).get("aliases"))
        setup_handlers(c, Handlers.commands, c_parser)

    return parser

def setup_handlers(command:str, commands: dict, parser: argparse.ArgumentParser):
    c_args = commands.get(command).get("args")
    if c_args is not None:
        for a in commands.get(command).get("args"):
            parser.add_argument(a.get("name"), metavar=a.get("metavar"))

    c_optionals = commands.get(command).get("optionals")
    if c_optionals is not None:
        for a in c_optionals:
            parser.add_argument(*a.get('flags'), dest=a.get("dest"), action="store")

    c_flags = commands.get(command).get("flags")
    if c_flags is not None:
        for a in c_flags:
            parser.add_argument(*a.get('flags'), dest=a.get("dest"), action="store_true")

def handle(context: Context, command: str) -> callable:
    for key in Handlers.commands:
        aliases = Handlers.commands.get(key).get("aliases")+[Handlers.commands.get(key).get("name")]
        if command in aliases:
            return Handlers.commands[key]["func"]

    context.profile = context.data.get_profile(context.args.get("command"))
    if context.profile is not None:
        for key in Handlers.profile_commands:
            aliases = Handlers.profile_commands.get('key').get("aliases")+[Handlers.profile_commands.get('key').get("name")]
            if command in aliases:
                return Handlers.profile_commands[key]["func"]
            
    return None


def cmd():

    data = Data()
    parser = setup_argparser(data)
    args = parser.parse_args()
    c = Context(vars(args), data)
    handler = handle(c, c.args.get("command"))
    if handler is not None:
        handler(c)


# fir <command> <options>
# fir <profile> <command> <options>