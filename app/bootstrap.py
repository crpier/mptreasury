import logging
import os
import sys
from pathlib import Path

import yaml
from yaml.loader import SafeLoader

from app import config

logger = logging.getLogger("mptreasury")
logger.setLevel(logging.DEBUG)

# TODO: set logging level in bootstrap()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# TODO: set db in bootstrap
def bootstrap(env="prod"):
    if env == "prod":
        conf_path = Path(os.path.expanduser("~/.config/mptreasury/conf.yaml"))
        conf_path.absolute()
        if not conf_path.exists():
            raise FileNotFoundError("Config file does not exist")
        with conf_path.open() as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))[0]
            conf = config.Config(**data)
    elif env == "e2e_test":
        conf = config.Config(LIBRARY_DIR="lol", DISCOGS_PAT="", APP_ENV="e2e_test")
    else:
        conf = config.Config()  # type: ignore
    return conf
