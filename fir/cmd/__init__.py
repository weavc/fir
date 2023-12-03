import argparse
import sys


from argcomplete import FilesCompleter


from fir import config
from fir.context import Context
from fir.cmd.base_commands import *
from fir.cmd.profile_commands import *
from fir.cmd.config_commands import *
from fir.data.profile import Profile
from fir.data.settings import Settings

handlers = [ProfileHandlers, ConfigHandlers, CommandHandlers]

class FirParser(argparse.ArgumentParser): 
   def error(self, message):
      sys.stderr.write('error: %s\n' % message)
      self.print_help()
      sys.exit(2)

def setup_argparser():
    parser = FirParser(description="Fir, command line task tracking")

    parser.add_argument("--verbose", "-v", action="store_true",
                        dest="verbose", help="Prints more information", default=False)
    parser.add_argument("--pretty", "-p", action="store_true",
                        dest="pretty", default=False)
    parser.add_argument("--debug", "-d", action="store_true",
                        dest="debug", default=False, help="Prints dedug info")
    parser.add_argument("--silent", action="store_true",
                        dest="silent", default=False, help="Don't print anything")
    parser.add_argument("--scope", action="store",
                        dest="scope", help="Use a specific profile to run this action")

    sub = parser.add_subparsers(dest="command", metavar="<command>")
    for h in handlers:
        if h.name is None:
            for c in h.commands:    
                setup_handlers(h.commands.get(c), sub)
        else:
            sub_parser = sub.add_parser(h.name, aliases=h.aliases, help=f"See: 'fir {h.name} --help'")
            sub_sub_parser = sub_parser.add_subparsers(dest="sub_command", metavar="<command>")
            for c in h.commands:
                setup_handlers(h.commands.get(c), sub_sub_parser)

    return parser


def setup_handlers(command: dict, sub: argparse.ArgumentParser):
    parser = sub.add_parser(command.get(
        "name"), aliases=command.get("aliases"), help=command.get("desc"))
    c_args = command.get("args")
    if c_args is not None:
        for a in command.get("args"):
            p = parser.add_argument(a.get("name"), metavar=a.get(
                "metavar"), nargs=a.get("nargs"), help=a.get("desc"))
            if a.get("name") == "path":
                p.completer = FilesCompleter()

    c_optionals = command.get("optionals")
    if c_optionals is not None:
        for a in c_optionals:
            parser.add_argument(*a.get('flags'), dest=a.get("dest"),
                                action="store", nargs=a.get("nargs"), help=a.get("desc"))

    c_flags = command.get("flags")
    if c_flags is not None:
        for a in c_flags:
            parser.add_argument(
                *a.get('flags'), dest=a.get("dest"), action="store_true", help=a.get("desc"))


def get_command(context: Context) -> dict:

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
        c.logger.log_error(f"Command not found", exit=False)
        parser.print_help()

