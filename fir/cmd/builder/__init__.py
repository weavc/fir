from copy import copy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CmdArg:
    name: str
    description: str = ""
    nargs: str = None
    aliases: list[str] = field(default_factory=list[str])

    def with_overrides(self, name: str = None, description: str = None, flags: list[str] = None, nargs: str = None):
        m = copy(self)
        if name is not None:
            m.name = name
        if description is not None:
            m.description = description
        if flags is not None:
            m.flags = flags
        if nargs is not None:
            m.nargs = nargs

        return m


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
