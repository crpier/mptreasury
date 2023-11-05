import os
from pathlib import Path

import yaml
from yaml.loader import SafeLoader

from app import config

# TODO: set db in bootstrap
def bootstrap(env="prod"):
    if env == "prod":
        conf_path = Path(os.path.expanduser("~/.config/mptreasury/conf.yaml"))
        conf_path.absolute()
        if not conf_path.exists():
            conf = config.Config()
        else:
            with conf_path.open() as f:
                data = list(yaml.load_all(f, Loader=SafeLoader))[0]
                conf = config.Config(**data)
    elif env == "e2e_test":
        conf = config.Config(
            LIBRARY_DIR=Path("lol"), DISCOGS_PAT="", APP_ENV="e2e_test"
        )
    else:
        conf = config.Config()

    conf.CACHE_FOLDER.mkdir(parents=True, exist_ok=True)
    return conf
