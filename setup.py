#!/usr/bin/env python

import os

from setuptools import setup, find_packages

_README_FILE = "./README.md"

with open(_README_FILE, "r") as file:
    long_description = file.read()

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(pjoin(here, "lifeomic_logging", "version.py")) as f:
    exec(f.read(), {}, version_ns)

setup(
    name="lifeomic_logging",
    version=version_ns["__version__"],
    description="LifeOmic Python Logging Library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lifeomic/logging-py",
    license="MIT",
    author="LifeOmic Development",
    author_email="development@lifeomic.com",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Utilities",
    ],
)
