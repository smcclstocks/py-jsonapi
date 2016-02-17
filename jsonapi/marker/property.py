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
jsonapi.marker.property
=======================

This module contains decorators for **properties**.

.. code-block:: python3

    class User(object):

        @attribute()
        def name(self):
            return self._name

        @name.setter
        def name(self, name):
            self._name = name.strip()
            return None

    # Using the *property* decorators will turn the methods into properties.
    user = User()
    user.name = "Homer"
    print(user.name)
"""

# local
from . import method


__all__ = [
    "attribute",
    "id_attribute",
    "to_one_relationship",
    "to_many_relationship"
]


# Attribute
# ~~~~~~~~~

class attribute(method.PropertyMixin, method.attribute):
    """
    The same as :class:`jsonapi.marker.method.attribute`,
    but emulates a Python `property()`.
    """


class id_attribute(method.PropertyMixin, method.id_attribute):
    """
    The same as :class:`jsonapi.marker.method.id_attribute`,
    but emulates a Python `property()`.
    """


# Relationships
# ~~~~~~~~~~~~~

class to_one_relationship(method.PropertyMixin, method.to_one_relationship):
    """
    The same as :class:`jsonapi.marker.method.to_one_relationship`,
    but emulates a Python `property()`.
    """


class to_many_relationship(method.PropertyMixin, method.to_many_relationship):
    """
    The same as :class:`jsonapi.marker.method.to_many_relationship`,
    but emulates a Python `property()`.
    """
