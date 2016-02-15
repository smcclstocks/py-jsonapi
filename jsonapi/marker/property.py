#!/usr/bin/env python3

"""
jsonapi.marker.property
=======================

:license: GNU Affero General Public License v3

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
