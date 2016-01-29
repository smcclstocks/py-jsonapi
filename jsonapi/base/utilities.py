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

"""
jsonapi.base.utilities
======================

This module contains some helpers, which are frequently needed in different
modules.
"""

# std
from collections import OrderedDict


__all__ = [
    "ensure_identifier_object",
    "ensure_identifier",
    "collect_identifiers"
]


def ensure_identifier_object(api, obj):
    """
    Returns the identifier object for the *resource*:

    .. code-block:: python3

        {
            "type": "people",
            "id": "42"
        }

    The object *obj* can be a two tuple ``(typename, id)``, a resource document
    which contains the *id* and *type* key ``{"type": ..., "id": ...}`` or
    a real resource object.

    :arg jsonapi.base.api.API api:
    :arg obj:
    """
    if isinstance(obj, tuple):
        d = OrderedDict()
        d["type"] = obj[0]
        d["id"] = obj[1]
        return d
    elif isinstance(obj, dict):
        # The dictionary may contain more keys than only +id* and *type*. So
        # we extract only these two keys.
        d = OrderedDict()
        d["type"] = obj["type"]
        d["id"] = obj["id"]
        return d
    else:
        typename = api.get_typename(obj)
        serializer = api.get_serializer(typename)
        return serializer.serialize_identifier(obj)


def ensure_identifier(api, obj):
    """
    Does the same as :func:`ensure_identifier_object`, but returns the two
    tuple identifier object instead of the document:

    .. code-block:: python3

        # (typename, id)
        ("people", "42")

    :arg jsonapi.base.api.API api:
    :arg obj:
    """
    if isinstance(obj, tuple):
        assert len(obj) == 2
        return obj
    elif isinstance(obj, dict):
        return (obj["type"], obj["id"])
    else:
        typename = api.get_typename(obj)
        serializer = api.get_serializer(typename)
        return serializer.full_id(obj)


def collect_identifiers(d):
    """
    Walks through the document *d* and saves all type identifers. This means,
    that each time a dictionary in *d* contains a *type* and *id* key, this
    pair is added to a set and later returned:

    .. code-block:: python3

        >>> d = {
        ...     "author": {
        ...         "data": {"type": "User", "id": "42"}
        ...     }
        ...     "comments": {
        ...         "data": [
        ...             {"type": "Comment", "id": "2"},
        ...             {"type": "Comment", "id": "3"}
        ...         ]
        ...     }
        ... }
        >>> collect_identifiers(d)
        {("User", "42"), ("Comment", "2"), ("Comment", "3")}
    """
    ids = set()
    docs = [d]
    while docs:
        d = docs.pop()

        if isinstance(d, list):
            for value in d:
                if isinstance(value, (dict, list)):
                    docs.append(value)

        elif isinstance(d, dict):
            if "id" in d and "type" in d:
                ids.add((d["type"], d["id"]))

            for value in d.values():
                if isinstance(value, (dict, list)):
                    docs.append(value)
    return ids
