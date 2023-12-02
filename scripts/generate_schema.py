from marshmallow import Schema, fields
import tomllib
import tomli_w
import os
from fir.config import DATA_DIR

from fir.data import Data

d = Data()
data = d.get_data()


t = Schema.from_dict(data)

print(t)
