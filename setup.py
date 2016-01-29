#!/usr/bin/env python3

# py-jsonapi - A toolkit for building a JSONapi
# Copyright (C) 2016 Benedikt Schmitt <benedikt@benediktschmitt.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
