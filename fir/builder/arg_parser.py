
import argparse
from fir.builder import Cmd, CmdBuilder


class ArgParserSetup:

    handlers: list[CmdBuilder]

    def __init__(self, *handlers: CmdBuilder):
        self.handlers = handlers

    def configure_argparser(self, parser: argparse.ArgumentParser):
        sub = parser.add_subparsers(dest="command", metavar="<command>")
        for h in self.handlers:
            if h.name is None:
                for c in h.cmds:
                    self.setup_handlers(h.cmds.get(c), sub)
            else:
                sub_parser = sub.add_parser(h.name, aliases=h.aliases, help=f"See: 'fir {h.name} --help'")
                sub_sub_parser = sub_parser.add_subparsers(dest="sub_command", metavar="<command>")
                for c in h.cmds:
                    self.setup_handlers(h.cmds.get(c), sub_sub_parser)

    def setup_handlers(self, command: Cmd, sub: argparse.ArgumentParser):
        parser = sub.add_parser(command.name, aliases=command.aliases, help=command.description)
        for a in command.args:
            p = parser.add_argument(a.name, nargs=a.nargs, help=a.description)

        for a in command.optionals:
            parser.add_argument(*a.aliases, dest=a.name, action="store", nargs=a.nargs, help=a.description)

        for a in command.flags:
            parser.add_argument(*a.aliases, dest=a.name, action="store_true", help=a.description)

    def get_command(self, args: dict) -> Cmd | None:

        for h in self.handlers:
            if h.name is None:
                for c in h.cmds:
                    command: Cmd = h.cmds.get(c)
                    aliases = command.aliases + [command.name]
                    if args.get("command") in aliases:
                        return command
            else:
                if args.get("command") == h.name:
                    for c in h.cmds:
                        command: Cmd = h.cmds.get(c)
                        aliases = command.aliases + [command.name]
                        if args.get("sub_command") in aliases:
                            return command

        return None
