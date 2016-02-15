#!/usr/bin/env python3

"""
:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>
"""

# std
from setuptools import setup

# local
import jsonapi


try:
    long_description = open("README.rst").read()
except OSError:
    long_description = "not available"

try:
    license_ = open("LICENSE").read()
except OSError:
    license_ = "not available"

setup(
    name = "py-jsonapi",
    version = jsonapi.version.version,
    description = "A toolkit for building a JSONapi",
    long_description = long_description,
    author = "Benedikt Schmitt",
    author_email = "benedikt@benediktschmitt.de",
    url = "https://github.com/benediktschmitt/py-jsonapi",
    download_url = "https://github.com/benediktschmitt/py-jsonapi/archive/master.zip",
    packages = [
        "jsonapi",
        "jsonapi.base",
        "jsonapi.base.handler",
        "jsonapi.flask",
        "jsonapi.marker",
        "jsonapi.mongoengine",
        "jsonapi.sqlalchemy",
        "jsonapi.tornado"
    ],
    license = license_,
    install_requires = [
        "cached_property"
    ],
    include_package_data = True,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries"
    ]
)
