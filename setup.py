#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2016 Benedikt Schmitt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
        "jsonapi.asyncio",
        "jsonapi.asyncio.handler",
        "jsonapi.flask",
        "jsonapi.marker",
        "jsonapi.mongoengine",
        "jsonapi.motorengine",
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries"
    ]
)
