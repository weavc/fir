class Args:
    __args: dict

    def __init__(self, args: dict) -> None:
        self.__args = args

    def get(self, arg: str, default=None):
        val = self.__args.get(arg, default)
        if val is None:
            return default
        return val

    def keys(self):
        return self.__args.keys()

    def as_dict(self):
        return self.__args
