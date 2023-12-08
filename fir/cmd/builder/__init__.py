from copy import copy
from dataclasses import dataclass, field
from typing import Callable


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

    func: Callable = None


class CmdWrapper:
    cmd: Cmd

    def __init__(self, cmd: Cmd):
        self.cmd = cmd

    def with_positional(self, *parameters: CmdArg):
        self.cmd.args.extend(parameters)
        return self

    def with_optional(self, *parameters: CmdArg):
        self.cmd.optionals.extend(parameters)
        return self

    def with_flag(self, *parameters: CmdArg):
        self.cmd.flags.extend(parameters)
        return self


class CmdBuilder:
    name: str
    aliases: list[str]
    cmds: dict[str, Cmd] = {}

    def register(self, name: str, func: Callable, description: str = None, aliases: list[str] = []):
        cmd = Cmd(name, description=description, aliases=aliases)
        self.__register(cmd, func)
        return CmdWrapper(self.cmds[cmd.func.__name__])

    def __register(self, cmd, func: Callable = None):
        if func is not None:
            cmd.func = func

        self.cmds[cmd.func.__name__] = cmd
