from dataclasses import dataclass, field
from typing import Any


@dataclass
class CmdArg:
    name: str
    description: str = ""
    nargs: str = None
    aliases: list[str] = field(default_factory=list[str])

    def with_overrides(self, name: str = None, description: str = None, flags: list[str] = None, nargs: str = None):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if flags is not None:
            self.flags = flags
        if nargs is not None:
            self.nargs = nargs

        return self


@dataclass
class Cmd:
    name: str
    description: str = None
    aliases: list[str] = field(default_factory=list[str])
    args: list[CmdArg] = field(default_factory=list[CmdArg])
    optionals: list[CmdArg] = field(default_factory=list[CmdArg])
    flags: list[CmdArg] = field(default_factory=list[CmdArg])

    func: Any = None  # Look for a better way to define functions (like delegates in c#?)


class CmdWrapper:
    cmd: Cmd

    def __init__(self, cmd: Cmd):
        self.cmd = cmd

    def add_positional(self, *parameters: CmdArg):
        self.cmd.args.extend(parameters)
        return self

    def add_optional(self, *parameters: CmdArg):
        self.cmd.optionals.extend(parameters)
        return self

    def add_optional_flag(self, *parameters: CmdArg):
        self.cmd.flags.extend(parameters)
        return self


class CmdBuilder:
    name: str
    aliases: list[str]
    cmds: dict[str, Cmd] = {}

    def register_command(self, cmd: Cmd, func: Any = None):
        self.__register(cmd, func)
        return CmdWrapper(self.cmds[cmd.func.__name__])

    def register_commands(self, *cmd: Cmd):
        for c in cmd:
            self.__register(c)

    def __register(self, cmd, func=None):
        if func is not None:
            cmd.func = func

        self.cmds[cmd.func.__name__] = cmd


class CmdBuilderDecorators(CmdBuilder):

    @classmethod
    def command(self, cmd: Cmd):
        def decorator(func):

            # workaround for decorator ordering:
            if self.cmds.get(func.__name__, None) is not None:
                cmd.args = self.cmds[func.__name__].args
                cmd.optionals = self.cmds[func.__name__].optionals
                cmd.flags = self.cmds[func.__name__].flags

            cmd.func = func
            self.cmds[func.__name__] = cmd
            return func
        return decorator

    @classmethod
    def add_positional(self, *parameters: CmdArg):
        def decorator(func):
            self.get_cmd_or_default(func.__name__).args.extend(parameters)
            return func
        return decorator

    @classmethod
    def add_optional(self, *parameters: CmdArg):
        def decorator(func):
            self.get_cmd_or_default(func.__name__).optionals.extend(parameters)
            return func
        return decorator

    @classmethod
    def add_optional_flag(self, *parameters: CmdArg):
        def decorator(func):
            self.get_cmd_or_default(func.__name__).flags.extend(parameters)
            return func
        return decorator

    @classmethod
    def get_cmd_or_default(self, name: str):
        if self.cmds.get(name) is None:
            self.cmds[name] = Cmd("default")

        return self.cmds[name]
