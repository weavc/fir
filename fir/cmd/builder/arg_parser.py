
import argparse
from fir.cmd.builder import Cmd, CmdBuilder


class ArgParserSetup:

    handlers: list[CmdBuilder]
    print_help: bool

    def __init__(self, *handlers: CmdBuilder, print_help: bool = False):
        self.handlers = handlers
        self.print_help = print_help

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

    def setup_handlers(self, command: Cmd, sub: argparse.ArgumentParser, parser = None):
        if parser is None:
            parser = sub.add_parser(command.name, aliases=command.aliases, help=command.description)
        for a in command.args:
            parser.add_argument(a.name, nargs=a.nargs, help=a.description)

        for a in command.optionals:
            parser.add_argument(*a.aliases, dest=a.name, action="store", nargs=a.nargs, help=a.description)

        for a in command.flags:
            parser.add_argument(*a.aliases, dest=a.name, action="store_true", help=a.description)

    def get_command(self, args: dict) -> Cmd | None:
        command = args.get("command")
        handler = self.__handler_or_default(command)
        if handler is None:
            return
        
        if handler.name is None:
            sub_command = command
        else:
            sub_command = args.get("sub_command")
    
        for c in handler.cmds:
            cmd: Cmd = handler.cmds.get(c)
            aliases = cmd.aliases + [cmd.name]
            if sub_command in aliases:
                return cmd

        return None

    def __handler_or_default(self, c: str):
        h = None
        none_handlers = [h for h in self.handlers if h.name == None]
        if len(none_handlers) > 0:
            h = none_handlers.pop()

        handlers = [h for h in self.handlers if h.name == c]
        if len(handlers) > 0:
            h = handlers.pop()

        return h