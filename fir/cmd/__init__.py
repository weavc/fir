import argparse
import sys

from fir import config
from fir.cmd.builder.arg_parser import ArgParserSetup, get_parser
from fir.cmd.set_commands import SetHandlers
from fir.cmd.status_commands import StatusHandlers
from fir.context import Context
from fir.cmd.base_commands import CommandHandlers
from fir.cmd.profile_commands import ProfileHandlers
from fir.cmd.config_commands import ConfigHandlers
from fir.data.profile import Profile
from fir.data.settings import Settings


def cmd():
    s = Settings()
    c = Context()

    setup = ArgParserSetup(
        CommandHandlers(c),
        ConfigHandlers(c),
        ProfileHandlers(c),
        StatusHandlers(c),
        SetHandlers(c))
    
    parser = setup.configure_argparser(parser)

    args = vars(parser.parse_args())
    scope = s.data.scope

    if args.get("scope"):
        scope = args.get("scope")

    _, profile_path = s.get_profile(scope)
    p = Profile(profile_path, read=False)
    c.setup(args, p, s)

    c.logger.log_debug(f"Args: {c.args.as_dict()}")
    c.logger.log_debug(f"Env: {config.ENV}")

    command = setup.get_command(c.args.as_dict())
    if command is not None:
        c.logger.log_info(f"Running command: {command.name}")
        command.func()
    else:
        c.logger.log_error("Command not found", exit=False)
        parser.print_help()
