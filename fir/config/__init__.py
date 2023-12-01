import os

if os.getenv("POETRY_ACTIVE") == "1" and __file__.startswith(os.getcwd()):
    from fir.config.env_dev import *
else:
    from fir.config.env_prod import *