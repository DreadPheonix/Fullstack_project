import os
import pathlib
import pandas as pd

import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from config import load_config


BASE_DIR = pathlib.Path(__file__).parent.parent
CONFIG = load_config()
PATHS = CONFIG["paths"]
DATASET_DIR = BASE_DIR / PATHS["dataset_directory"]


def parquet_needs_refresh(csv_path: pathlib.Path, parquet_path: pathlib.Path) -> bool:
    if not parquet_path.exists():
        return True
    return os.path.getmtime(csv_path) > os.path.getmtime(parquet_path)


def convert_dataset() -> None:
    for source in PATHS["local_datasets"]:
        csv_path = DATASET_DIR / source["csv"]
        parquet_path = DATASET_DIR / source["parquet"]
        if not csv_path.exists():
            print(f"CSV file not found: {csv_path}")
            continue
        if not parquet_needs_refresh(csv_path, parquet_path):
            print(f"Parquet file {parquet_path.name} is up to date.")
            continue
        dataset = pd.read_csv(csv_path)
        dataset.to_parquet(parquet_path, index=False)
        print(f"Converted {csv_path.name} to {parquet_path.name}")


if __name__ == "__main__":
    convert_dataset()
