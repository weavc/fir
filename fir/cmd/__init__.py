import argparse


from argcomplete import FilesCompleter


from fir import config
from fir.context import Context
from fir.cmd.base_commands import *
from fir.cmd.profile_commands import *
from fir.cmd.config_commands import *
from fir.data.profile import Profile
from fir.data.settings import Settings

handlers = [ProfileHandlers, ConfigHandlers, CommandHandlers]


def setup_argparser():
    parser = argparse.ArgumentParser(
        description="Fir, command line task tracking")
    parser.add_argument("--verbose", "-v", action="store_true",
                        dest="verbose", help="Prints more information", default=False)
    parser.add_argument("--pretty", "-p", action="store_true",
                        dest="pretty", default=False)
    parser.add_argument("--debug", "-d", action="store_true",
                        dest="debug", default=False)
    parser.add_argument("--silent", action="store_true",
                        dest="silent", default=False)
    parser.add_argument("--scope", "-s", action="store",
                        dest="scope")

    sub = parser.add_subparsers(dest="command", metavar="action")

    for h in handlers:
        if h.name is None:
            for c in h.commands:
                setup_handlers(h.commands.get(c), sub)
        else:
            sub_parser = sub.add_parser(h.name, aliases=h.aliases)
            sub_sub_parser = sub_parser.add_subparsers(
                dest="sub_command", metavar="action")
            for c in h.commands:
                setup_handlers(h.commands.get(c), sub_sub_parser)

    return parser


def setup_handlers(command: dict, sub: argparse.ArgumentParser):
    parser = sub.add_parser(command.get(
        "name"), aliases=command.get("aliases"))
    c_args = command.get("args")
    if c_args is not None:
        for a in command.get("args"):
            p = parser.add_argument(a.get("name"), metavar=a.get(
                "metavar"), nargs=a.get("nargs"))
            if a.get("name") == "path":
                p.completer = FilesCompleter()

    c_optionals = command.get("optionals")
    if c_optionals is not None:
        for a in c_optionals:
            parser.add_argument(*a.get('flags'), dest=a.get("dest"),
                                action="store", nargs=a.get("nargs"))

    c_flags = command.get("flags")
    if c_flags is not None:
        for a in c_flags:
            parser.add_argument(
                *a.get('flags'), dest=a.get("dest"), action="store_true")


def get_command(context: Context) -> dict:
    # scope = context.args.get("scope")
    # profile = context.data.get_profile(scope)
    # if profile is None:
    #     context.logger.log_error(f"Profile not found: {scope}. Please set a new profile with 'fir profile <profile>'")
    #     return None

    # context.profile = profile

    for h in handlers:
        if h.name is None:
            for c in h.commands:
                command = h.commands.get(c)
                aliases = command.get("aliases") + [command.get("name")]
                if context.args.get("command") in aliases:
                    return command
        else:
            if context.args.get("command") == h.name:
                for c in h.commands:
                    command = h.commands.get(c)
                    aliases = command.get("aliases") + [command.get("name")]
                    if context.args.get("sub_command") in aliases:
                        return command

    return None


def cmd():
    s = Settings()

    parser = setup_argparser()
    args = vars(parser.parse_args())
    scope = s.data.scope

    if args.get("scope"):
        scope = args.get("scope")

    _, profile_path = s.get_profile(scope)

    p = Profile(profile_path)
    c = Context(args, p, s)

    c.logger.log_debug(f"Args: {c.args}")
    c.logger.log_debug(f"Env: {config.ENV}")

    command = get_command(c)
    if command is not None:
        c.logger.log_info(f"Running command: {command.get('name')}")
        command["func"](c)
    else:
        c.logger.log_error(f"Command not found")
