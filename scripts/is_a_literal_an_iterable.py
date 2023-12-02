from typing import get_args
from fir.types import ConfigOptions

# Answer: no, but with typing.get_args it can be
for o in get_args(ConfigOptions):
    print(o)
