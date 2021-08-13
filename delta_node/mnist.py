import os
import shutil
import gzip
from typing import IO
import requests
import struct
import numpy as np
from tempfile import TemporaryFile

from . import config


URL_PREFIX = "https://dataset.bj.bcebos.com/mnist/"
TEST_IMAGE_URL = URL_PREFIX + "t10k-images-idx3-ubyte.gz"
TEST_LABEL_URL = URL_PREFIX + "t10k-labels-idx1-ubyte.gz"
TRAIN_IMAGE_URL = URL_PREFIX + "train-images-idx3-ubyte.gz"
TRAIN_LABEL_URL = URL_PREFIX + "train-labels-idx1-ubyte.gz"


def read_mnist(image_fileobj: IO[bytes], label_fileobj: IO[bytes]):
    with gzip.GzipFile(fileobj=image_fileobj, mode="rb") as image_file, gzip.GzipFile(
        fileobj=label_fileobj, mode="rb"
    ) as label_file:
        image_buf = image_file.read()
        label_buf = label_file.read()

        step_label = 0

        offset_img = 0
        # read from Big-endian
        # get file info from magic byte
        # image file : 16B
        magic_byte_img = ">IIII"
        magic_img, image_num, rows, cols = struct.unpack_from(
            magic_byte_img, image_buf, offset_img
        )
        offset_img += struct.calcsize(magic_byte_img)

        offset_lab = 0
        # label file : 8B
        magic_byte_lab = ">II"
        magic_lab, label_num = struct.unpack_from(magic_byte_lab, label_buf, offset_lab)
        offset_lab += struct.calcsize(magic_byte_lab)

        buffer_size = 100
        while True:
            if step_label >= label_num:
                break
            fmt_label = ">" + str(buffer_size) + "B"
            labels = struct.unpack_from(fmt_label, label_buf, offset_lab)
            offset_lab += struct.calcsize(fmt_label)
            step_label += buffer_size

            fmt_images = ">" + str(buffer_size * rows * cols) + "B"
            images_temp = struct.unpack_from(fmt_images, image_buf, offset_img)
            images = np.reshape(images_temp, (buffer_size, rows * cols)).astype(
                "float32"
            )
            offset_img += struct.calcsize(fmt_images)

            for i in range(buffer_size):
                yield images[i, :], int(labels[i])


def download_mnist(image_url: str, label_url: str):
    with TemporaryFile(mode="w+b") as img_file, TemporaryFile(mode="w+b") as label_file:
        resp = requests.get(image_url, stream=True)
        resp.raise_for_status()
        shutil.copyfileobj(resp.raw, img_file)
        img_file.seek(0)

        resp = requests.get(label_url, stream=True)
        resp.raise_for_status()
        shutil.copyfileobj(resp.raw, label_file)
        label_file.seek(0)

        for i, (img, label) in enumerate(read_mnist(img_file, label_file)):
            img_filename = os.path.join(
                config.data_dir, "mnist", f"{label}", f"{i}.npy"
            )
            img_dir, _ = os.path.split(img_filename)
            if not os.path.exists(img_dir):
                os.makedirs(img_dir, exist_ok=True)
            np.save(img_filename, img)


def mnist_train():
    download_mnist(TRAIN_IMAGE_URL, TRAIN_LABEL_URL)


def mnist_test():
    download_mnist(TEST_IMAGE_URL, TEST_LABEL_URL)
