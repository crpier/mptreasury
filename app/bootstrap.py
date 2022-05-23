import os
from pathlib import Path
from app import config
import yaml
from yaml.loader import SafeLoader


def bootstrap(env="prod"):
    if env == "prod":
        conf_path = Path(os.path.expanduser("~/.config/mptreasury/conf.yaml"))
        conf_path.absolute()
        if not conf_path.exists():
            raise FileNotFoundError("Config file does not exist")
        with conf_path.open() as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))[0]
            conf = config.Config(**data)
    else:
        conf = config.Config()  # type: ignore
    return conf

