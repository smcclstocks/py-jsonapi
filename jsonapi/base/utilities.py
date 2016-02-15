#!/usr/bin/env python3

"""
jsonapi.base.utilities
======================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

This module contains some helpers, which are frequently needed in different
modules.
"""

# std
from collections import OrderedDict

# local
from . import errors


__all__ = [
    "ensure_identifier_object",
    "ensure_identifier",
    "collect_identifiers",
    "relative_identifiers",
]


def ensure_identifier_object(obj):
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

    :arg obj:
    """
    # Identifier tuple
    if isinstance(obj, tuple):
        d = OrderedDict([
            ("type", obj[0]),
            ("id", obj[1])
        ])
        return d
    # JSONapi identifier object
    elif isinstance(obj, dict):
        # The dictionary may contain more keys than only *id* and *type*. So
        # we extract only these two keys.
        d = OrderedDict([
            ("type", obj["type"]),
            ("id", obj["id"])
        ])
        return d
    # obj is a resource resource
    else:
        schema = obj._jsonapi["schema"]
        d = OrderedDict([
            ("typename", schema.typename),
            ("id", schema.id_attribute.get(obj))
        ])
        return d


def ensure_identifier(obj):
    """
    Does the same as :func:`ensure_identifier_object`, but returns the two
    tuple identifier object instead of the document:

    .. code-block:: python3

        # (typename, id)
        ("people", "42")

    :arg obj:
    """
    if isinstance(obj, tuple):
        assert len(obj) == 2
        return obj
    elif isinstance(obj, dict):
        return (obj["type"], obj["id"])
    else:
        schema = obj._jsonapi["schema"]
        return (schema.typename, schema.id_attribute.get(obj))


def collect_identifiers(d, include_meta=False):
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

    :arg dict d:
    :arg bool include_meta:
        If true, we also look for (id, type) keys in the meta objects.
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

            for key, value in d.items():
                if key == "meta" and not include_meta:
                    continue
                if isinstance(value, (dict, list)):
                    docs.append(value)
    return ids


def relative_identifiers(relname, resource):
    """
    Returns a list with the ids of related resources.

    :arg str relname:
        The name of the relationship
    :arg resource:

    :raises jsonapi.base.errors.RelationshipNotFound:
    """
    schema = resource._jsonapi["schema"]
    relationship = schema.relationships.get(relname)
    if relationship is None:
        raise errors.RelationshipNotFound(schema.typename, relname)
    elif relationship.to_one:
        relative = relationship.get(resource)
        relatives = [relative] if relative else []
    else:
        relatives = relationship.get(resource)

    relatives = [ensure_identifier(relative) for relative in relatives]
    return relatives
