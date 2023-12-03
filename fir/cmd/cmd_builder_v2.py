
class CmdBuilderV2:

    @classmethod
    def command(cls, name, aliases=[], description=""):
        def decorator(func):
            cls.commands[func.__name__]["name"] = name
            cls.commands[func.__name__]["aliases"] = aliases
            cls.commands[func.__name__]["func"] = func
            cls.commands[func.__name__]["desc"] = description
            return func
        return decorator

    @classmethod
    def add_positional(cls, name: str, meta: str = None, nargs: str = None, description: str = ""):
        def decorator(func):
            args = cls.commands[func.__name__].get("args")
            if args is None:
                args = []

            pos = {"name": name, "metavar": meta, "nargs": nargs, "desc": description}
            args.append(pos)
            cls.commands[func.__name__]["args"] = args
            return func
        return decorator

    @classmethod
    def add_optional(cls, dest: str, *flags: str, nargs: str = None, description: str = ""):
        def decorator(func):
            args = cls.commands[func.__name__].get("optionals")
            if args is None:
                args = []

            pos = {"dest": dest, "flags": flags, "nargs": nargs, "desc": description}

            args.append(pos)
            cls.commands[func.__name__]["optionals"] = args
            return func
        return decorator

    @classmethod
    def add_optional_flag(cls, dest: str, *flags: str, description: str = ""):
        def decorator(func):
            args = cls.commands[func.__name__].get("flags")
            if args is None:
                args = []

            pos = {"dest": dest, "flags": flags, "desc": description}

            args.append(pos)
            cls.commands[func.__name__]["flags"] = args
            return func
        return decorator

    @classmethod
    def get_command_names(cls):
        return [cls.commands[c].get("name") for c in cls.commands if cls.commands[c].get("name")]
