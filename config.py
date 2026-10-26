import json
import pathlib
from typing import Any


CONFIG_PATH = pathlib.Path(__file__).with_name("config.json")


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return json.load(config_file)
