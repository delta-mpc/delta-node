from .mnist import mnist_train
from .wages import make_wage_df

import os
from delta_node import config

import pkgutil

__all__ = ["get_mnist", "get_wages", "get_iris", "get_spector", "get_all"]


def get_mnist():
    mnist_train()


def get_wages():
    make_wage_df()


def get_iris():
    data = pkgutil.get_data(__name__, "iris.csv")
    if data is None:
        raise ValueError("cannot read dataset iris")
    filename = os.path.join(config.data_dir, "iris.csv")
    with open(filename, mode="wb") as f:
        f.write(data)


def get_spector():
    data = pkgutil.get_data(__name__, "spector.csv")
    if data is None:
        raise ValueError("cannot read dataset spector")
    filename = os.path.join(config.data_dir, "spector.csv")
    with open(filename, mode="wb") as f:
        f.write(data)


def get_all():
    get_mnist()
    get_wages()
    get_iris()
    get_spector()
