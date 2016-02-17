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
jsonapi.base
============

This is the *base* of the *py-jsonapi* library. It contains the definition for
interfaces (database, serializer), which can be overridden and then used by an
API instance.

.. automodule:: jsonapi.base.handler
.. automodule:: jsonapi.base.api
.. automodule:: jsonapi.base.database
.. automodule:: jsonapi.base.errors
.. automodule:: jsonapi.base.pagination
.. automodule:: jsonapi.base.request
.. automodule:: jsonapi.base.response
.. automodule:: jsonapi.base.schema
.. automodule:: jsonapi.base.serializer
.. automodule:: jsonapi.base.utilities
.. automodule:: jsonapi.base.validators
"""

# local
from . import handler
from . import api
from . import database
from . import errors
from .request import Request
from .response import Response
from . import schema
from . import serializer
from . import utilities
from . import validators
