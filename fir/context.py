from fir.data.profile import Profile
from fir.data.settings import Settings
from fir.logger import Logger


class Context:
    profile: Profile
    settings: Settings
    args: tuple[str, dict]
    logger: Logger

    def __init__(self, args: dict, profile: Profile, settings: Settings):
        self.profile = profile
        self.settings = settings
        self.args = args
        self.logger = Logger(verbose=args.get("verbose"),
                             pretty=args.get("pretty"),
                             silent=args.get("silent"),
                             debug=args.get("debug"))
