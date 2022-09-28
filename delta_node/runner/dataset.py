from __future__ import annotations

import os
from typing import List

from delta_node import config


def check_datasets(datasets: List[str]):
    return all(
        os.path.exists(os.path.join(config.data_dir, dataset)) for dataset in datasets
    )
