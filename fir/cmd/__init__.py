import argparse
import sys


from argcomplete import FilesCompleter


from fir import config
from fir.builder.arg_parser import ArgParserSetup
from fir.context import Context
from fir.cmd.base_commands import *
from fir.cmd.profile_commands import *
from fir.cmd.config_commands import *
from fir.data.profile import Profile
from fir.data.settings import Settings


class FirParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def cmd():
    s = Settings()

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

    setup = ArgParserSetup(CommandHandlers(), ConfigHandlers(), ProfileHandlers())

    setup.configure_argparser(parser)

    args = vars(parser.parse_args())
    scope = s.data.scope

    if args.get("scope"):
        scope = args.get("scope")

    _, profile_path = s.get_profile(scope)

    p = Profile(profile_path)
    c = Context(args, p, s)

    c.logger.log_debug(f"Args: {c.args}")
    c.logger.log_debug(f"Env: {config.ENV}")

    command = setup.get_command(args)
    if command is not None:
        c.logger.log_info(f"Running command: {command.name}")
        command.func(c)
    else:
        c.logger.log_error(f"Command not found", exit=False)
        parser.print_help()
