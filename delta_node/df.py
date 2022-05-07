import os

import numpy as np
import pandas as pd

from delta_node import config



def random_df() -> pd.DataFrame:
    arr = np.random.randint(1, 10, size=(3, 2), dtype=np.int32)
    df = pd.DataFrame(arr, columns=["a", "b"])
    return df


def make_dfs():
    df1_path = os.path.join(config.data_dir, "df1.csv")
    df2_path = os.path.join(config.data_dir, "df2.csv")
    if not os.path.exists(df1_path):
        df1 = random_df()
        df1.to_csv(df1_path, index=False)
    if not os.path.exists(df2_path):
        df2 = random_df()
        df2.to_csv(df2_path, index=False)
