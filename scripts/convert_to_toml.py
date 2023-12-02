import tomllib
import tomli_w
import os
from fir.config import DATA_DIR

from fir.data import Data

d = Data()
data = d.get_data()
print(data)

with open(os.path.join(DATA_DIR, "profiles.toml"), "wb") as f:
    toml = tomli_w.dump(data, f)

print(toml)
