from fir.data import Data
from fir.helpers.logger import Logger

class Context:
    data: Data
    args: tuple[str, dict]
    logger: Logger

    def __init__(self, args: dict, data: Data):
        self.data = data
        self.args = args
        self.logger = Logger(verbose=args.get("verbose"), 
                             pretty=args.get("pretty"), 
                             silent=args.get("silent"), 
                             debug=args.get("debug"))
    
    @property
    def profile(self) -> dict:
        return self._profile

    @profile.setter
    def profile(self, value: dict) -> None:
        self._profile = value

    def get_task(self, task: str) -> dict:
        for t in self.profile.get("tasks"):
            if task in t.get("id"):
                return t
        return None