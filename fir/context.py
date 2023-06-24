
from fir.data import Data


class Context:
    data: Data
    args: dict

    def __init__(self, args: dict, data: Data):
        self.data = data
        self.args = args
    
    @property
    def profile(self) -> dict:
        return self._profile

    @profile.setter
    def profile(self, value) -> dict:
        self._profile = value