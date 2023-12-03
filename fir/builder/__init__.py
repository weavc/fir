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
    description: str
    aliases: list[str] = field(default_factory=list[str])
    args: list[CmdArg] = field(default_factory=list[CmdArg], init=False)
    optionals: list[CmdArg] = field(default_factory=list[CmdArg], init=False)
    flags: list[CmdArg] = field(default_factory=list[CmdArg], init=False)

    func: Any = field(init=False)  # Look for a better way to define functions (like delegates in c#?)


class CmdBuilderV2:
    name: str
    aliases: list[str]
    cmds: dict[str, Cmd] = {}

    @classmethod
    def command(cls, cmd: Cmd):
        def decorator(func):
            cmd.func = func
            cls.cmds[func.__name__] = cmd
            return func
        return decorator

    @classmethod
    def add_positional(cls, *parameters: CmdArg):
        def decorator(func):
            cls.cmds[func.__name__].args.extend(parameters)
            return func
        return decorator

    @classmethod
    def add_optional(cls, *parameters: CmdArg):
        def decorator(func):
            cls.cmds[func.__name__].optionals.extend(parameters)
            return func
        return decorator

    @classmethod
    def add_optional_flag(cls, *parameters: CmdArg):
        def decorator(func):
            cls.cmds[func.__name__].flags.extend(parameters)
        return decorator
