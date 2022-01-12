import gzip
import os
import random
import struct
from tempfile import TemporaryFile
from typing import IO

import numpy as np
import httpx
from tqdm import tqdm

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

        assert image_num == label_num
        yield label_num

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


def download_mnist(image_url: str, label_url: str, ratio: float = 1):
    with TemporaryFile(mode="w+b") as img_file, TemporaryFile(mode="w+b") as label_file, httpx.Client() as client:
        with client.stream("GET", image_url) as img_resp, client.stream("GET", label_url) as label_resp:
            img_resp.raise_for_status()
            img_size = int(img_resp.headers.get("content-length", 0))

            label_resp.raise_for_status()
            label_size = int(label_resp.headers.get("content-length", 0))

            total_size = img_size + label_size
            print("downloading mnist dataset")
            process_bar = tqdm(total=total_size, unit="iB", unit_scale=True)

            chunk_size = 1024
            for data in img_resp.iter_bytes(chunk_size):
                img_file.write(data)
                process_bar.update(len(data))
            img_file.seek(0)
            for data in label_resp.iter_bytes(chunk_size):
                label_file.write(data)
                process_bar.update(len(data))
            label_file.seek(0)

            process_bar.close()

        reader = read_mnist(img_file, label_file)
        img_count = next(reader)
        print("unpacking mnist dataset")
        process_bar = tqdm(total=img_count)
        for i, (img, label) in enumerate(reader):
            img_filename = os.path.join(
                config.data_dir, "mnist", f"{label}", f"{i}.npy"
            )
            img_dir, _ = os.path.split(img_filename)
            if not os.path.exists(img_dir):
                os.makedirs(img_dir, exist_ok=True)
            if random.random() < ratio:
                np.save(img_filename, img)
            process_bar.update(1)
        process_bar.close()


def mnist_train():
    if not os.path.exists(os.path.join(config.data_dir, "mnist")):
        download_mnist(TRAIN_IMAGE_URL, TRAIN_LABEL_URL, 0.67)


def mnist_test():
    if not os.path.exists(os.path.join(config.data_dir, "mnist")):
        download_mnist(TEST_IMAGE_URL, TEST_LABEL_URL, 0.67)
