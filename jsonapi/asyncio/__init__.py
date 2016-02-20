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

"""
jsonapi.asyncio
===============

.. hint::

    This package is basically a copy of ``jsonapi.base``, but adds to each
    database call an *await*:

    .. code-block:: python3

        # in jsonapi.base
        db.get_many()

        # in jsonapi.asyncio
        await db.get_many()

    This is is the only difference to the base API. If you know how to merge the
    *base* and *async* code, please create a pull request or tell me how to do
    it on GitHub. I don't like having so much redudante code :(

Contains an API base application for **asynchronous** database adapters.

.. automodule:: jsonapi.asyncio.api
.. automodule:: jsonapi.asyncio.database
.. automodule:: jsonapi.asyncio.handler
.. automodule:: jsonapi.asyncio.serializer
"""

# local
from . import api
from . import database
from . import handler
from . import serializer
