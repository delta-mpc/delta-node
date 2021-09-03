import os
from typing import Any, Callable, List, Tuple, Union, Dict
import random

import numpy as np
import pandas as pd
import torch
from PIL import Image, UnidentifiedImageError
from torch.utils.data import Dataset, DataLoader


class UnsupportedFileError(Exception):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def __str__(self) -> str:
        return f"unsupported file {self.filename}"


def load_file(
    filename: str,
) -> Union[np.ndarray, torch.Tensor, pd.DataFrame, Image.Image]:
    if not os.path.exists(filename):
        raise ValueError(f"{filename} does not exist")

    if filename.endswith(".npz"):
        result = np.load(filename)["arr_0"]
    elif filename.endswith(".npy"):
        result = np.load(filename)
    elif filename.endswith(".pt"):
        result = torch.load(filename)
    elif filename.endswith(".csv"):
        result = pd.read_csv(filename, sep=",")
    elif filename.endswith(".tsv") or filename.endswith(".txt"):
        result = pd.read_csv(filename, sep=r"\s+")
    elif filename.endswith(".xls") or filename.endswith(".xlsx"):
        result = pd.read_excel(filename)
    else:
        try:
            result = Image.open(filename)
        except UnidentifiedImageError:
            raise UnsupportedFileError(filename)
    return result


class FileDataset(Dataset):
    def __init__(self, filename: str, preprocess: Callable = None) -> None:
        result = load_file(filename)
        if isinstance(result, Image.Image):
            raise ValueError("file dataset does not support image file")
        self._result = result
        self._preprocess = preprocess

    def __getitem__(self, index):
        if isinstance(self._result, pd.DataFrame):
            item = self._result.iloc[index]
        else:
            item = self._result[index]

        if self._preprocess is not None:
            item = self._preprocess(item)
        return item

    def __len__(self) -> int:
        return len(self._result)


class DirectoryDataset(Dataset):
    def __init__(self, directory: str, preprocess: Callable = None) -> None:
        self._xs = []
        self._ys = []
        self._preprocess = preprocess
        root, dirnames, filenames = next(os.walk(directory))
        if len(filenames) > 0 and len(dirnames) == 0:
            self._xs.extend([os.path.join(root, filename) for filename in filenames])
        elif len(filenames) == 0 and len(dirnames) > 0:
            for dirname in dirnames:
                sub_root, sub_dirs, sub_files = next(
                    os.walk(os.path.join(root, dirname))
                )
                if len(sub_files) > 0 and len(sub_dirs) == 0:
                    self._xs.extend(
                        [os.path.join(sub_root, filename) for filename in sub_files]
                    )
                    self._ys.extend([dirname] * len(sub_files))
                else:
                    raise ValueError(
                        "directory can only contain files or sub directory that contains file"
                    )
        else:
            raise ValueError(
                "directory can only contain files or sub directory that contains file"
            )

    def __getitem__(self, index):
        filename = self._xs[index]
        x = load_file(filename)
        y = None
        if len(self._ys) > 0:
            y = self._ys[index]
        if self._preprocess is not None:
            if y is not None:
                x, y = self._preprocess(x, y)
            else:
                x = self._preprocess(x)
        if y is not None:
            return x, y
        return x

    def __len__(self) -> int:
        return len(self._xs)


class IndexLookUpDataset(Dataset):
    def __init__(self, indices: List[int], dataset: Dataset) -> None:
        self._indices = indices
        self._dataset = dataset

    def __getitem__(self, index):
        i = self._indices[index]
        return self._dataset[i]

    def __len__(self) -> int:
        return len(self._indices)


def new_dataloader(
    dataset_name: str, dataloader_cfg: Dict[str, Any], preprocess: Callable
):
    if not os.path.exists(dataset_name):
        raise ValueError(f"{dataset_name} does not exist")
    if os.path.isfile(dataset_name):
        dataset = FileDataset(dataset_name, preprocess)
    elif os.path.isdir(dataset_name):
        dataset = DirectoryDataset(dataset_name, preprocess)
    else:
        raise ValueError("dataset should be a file or a directory")
    dataloader = DataLoader(dataset, **dataloader_cfg)
    return dataloader


def split_dataset(
    dataset: Dataset, frac: float
) -> Tuple[IndexLookUpDataset, IndexLookUpDataset]:
    assert frac > 0 and frac < 1

    size = len(dataset)  # type: ignore
    frac_count = int(size * frac)
    indices = list(range(size))

    random.shuffle(indices)

    left_indices, right_indices = indices[:frac_count], indices[frac_count:]
    return IndexLookUpDataset(left_indices, dataset), IndexLookUpDataset(
        right_indices, dataset
    )


def new_train_val_dataloader(dataset_name: str, validate_frac: float, dataloader_cfg: Dict[str, Any], preprocess: Callable):
    assert "train" in dataloader_cfg, "dataloader_cfg should contain train"
    assert "validate" in dataloader_cfg, "dataloader_cfg should contain validate"

    if not os.path.exists(dataset_name):
        raise ValueError(f"{dataset_name} does not exist")
    if os.path.isfile(dataset_name):
        dataset = FileDataset(dataset_name, preprocess)
        val_dataset, train_dataset = split_dataset(dataset, validate_frac)
    elif os.path.isdir(dataset_name):
        train_path = os.path.join(dataset_name, "train")
        val_path = os.path.join(dataset_name, "val")
        if os.path.exists(train_path) and os.path.isdir(train_path) and os.path.exists(val_path) and os.path.isdir(val_path):
            train_root, train_dirs, train_files = next(os.walk(train_path))
            val_root, val_dirs, val_files = next(os.walk(val_path))
            if len(train_files) == 1 and len(val_files) == 1:
                train_dataset = FileDataset(os.path.join(train_root, train_files[0]), preprocess)
                val_dataset = FileDataset(os.path.join(val_root, val_files[0]), preprocess)
            else:
                train_dataset = DirectoryDataset(train_path)
                val_dataset = DirectoryDataset(val_path)
        else:
            dataset = DirectoryDataset(dataset_name, preprocess)
            val_dataset, train_dataset = split_dataset(dataset, validate_frac)
    else:
        raise ValueError("dataset should be a file or a directory")
    
    train_loader = DataLoader(train_dataset, **dataloader_cfg["train"])
    val_loader = DataLoader(val_dataset, **dataloader_cfg["validate"])
    return train_loader, val_loader