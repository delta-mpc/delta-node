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
    version="0.3.0",
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={"": [".gitignore"]},
    install_requires=[
    ],
    tests_require=["pytest"],
    cmdclass={"test": PyTest},
    test_suite="tests",
    entry_points={"console_scripts": ["delte_node_start=delta_node.main:main"]},
    zip_safe=False,
    author="miaohong",
    author_email="73902525@qq.com",
    description="delta node",
    python_requires=">=3.6",
)
