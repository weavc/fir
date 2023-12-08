from tabulate import tabulate
from termcolor import colored
from fir.utils.args import Args
from fir.data.profile import Profile
from fir.data.settings import Settings
from fir.utils import truncate
from fir.utils.logging.logger import Logger
from fir.types.dtos import TaskDto
from fir.utils.logging.profile_logging import ProfileLoggingExtensions


class Context:
    __profile: Profile
    __args: dict
    settings: Settings
    logger: Logger

    def __init__(self):
        pass

    def setup(self, args: dict, profile: Profile, settings: Settings):
        self.__profile = profile
        self.settings = settings
        self.__args = args
        self.logger = Logger(verbose=args.get("verbose"),
                             pretty=args.get("pretty"),
                             silent=args.get("silent"),
                             debug=args.get("debug"))

    @property
    def profile(self):
        if not self.__profile.has_read:
            self.__profile.read()
        return self.__profile
    
    @property
    def args(self) -> Args:
        return Args(self.__args)
    
    @property
    def logging(self):
        class LoggingExtensions:
            profile = ProfileLoggingExtensions(self.logger, self.profile)
        return LoggingExtensions

    def invalid_config_option(self):
        return self.logger.log_error(
            f"{self.args.get('config_name')} is not a valid option. Try 'fir config opts' for more information.")

    def link_profile(self, name: str, path: str):
        p = Profile(path)
        if p.data is None:
            return self.logger.log_error("Invalid profile")

        self.settings.data.profiles[name] = path
        self.settings.save()
