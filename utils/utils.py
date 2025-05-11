from pathlib import Path
from typing import Optional

import yaml


def load_yaml(config_path: str, relative_to: Optional[Path] = None) -> dict:
    if relative_to is None:
        path = Path(config_path)
    else:
        path = relative_to / config_path

    with open(path, "r") as f:
        return yaml.safe_load(f)
