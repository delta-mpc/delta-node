import os

import numpy as np
import pandas as pd

from delta_node import config


def random_wage_df() -> pd.DataFrame:
    arr = np.random.randint(3000, 8000, size=(3, 1), dtype=np.int32)
    df = pd.DataFrame(arr, columns=["wage"])
    return df


def make_wage_df():
    filename = os.path.join(config.data_dir, "wages.csv")
    if not os.path.exists(filename):
        df = random_wage_df()
        df.to_csv(filename, index=False)
