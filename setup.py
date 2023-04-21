# type: ignore
# -*- coding: utf-8 -*-
import shlex
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
        self.pytest_args = ["tests"] + shlex.split(self.pytest_args)

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name="delta_node",
    version="0.8.3",
    packages=find_packages(),
    package_data={"delta_node": ["dataset/examples/*.csv"]},
    include_package_data=True,
    exclude_package_data={"": [".gitignore"]},
    install_requires=[
        "aiosqlite==0.17.0",
        "async_lru==1.0.2",
        "cryptography==3.4.7",
        "delta-task==0.8.3",
        "fastapi==0.70.1",
        "grpclib==0.4.2",
        "httpx==0.23.0",
        "hypercorn==0.13.2",
        "numpy==1.22.0",
        "pandas==1.2.3",
        "Pillow==9.1.1",
        "protobuf==3.19.4",
        "pydantic==1.8.2",
        "pytest==6.2.5",
        "python-multipart==0.0.5",
        "PyYAML==6.0",
        "SQLAlchemy==1.4.21",
        "tqdm==4.46.0",
        "torch==1.8.2+cpu",
        "gmpy2==2.1.2",
        "streaming-form-data==1.11.0",
    ],
    tests_require=["pytest", "pytest-asyncio"],
    cmdclass={"test": PyTest},
    test_suite="tests",
    entry_points={"console_scripts": ["delta_node_start=delta_node.main:main"]},
    zip_safe=False,
    author="miaohong",
    author_email="73902525@qq.com",
    description="delta node",
    python_requires=">=3.6",
)
