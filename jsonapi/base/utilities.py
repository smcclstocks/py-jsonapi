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
        # The dictionary may contain more keys than only *id* and *type*. So
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


def relative_identifiers(api, resource, relname):
    """
    Returns a list with the ids of related resources.

    :arg jsonapi.base.api.API:
    :arg resource:
    :arg str relname:
        The name of the relationship

    :raises RelationshipNotFound:

    .. todo::

        Find a better name for this function.
    """
    typename = api.get_typename(resource)
    schema = api.get_schema(typename)
    relationship = schema.relationships.get(relname)
    if relationship is None:
        raise errors.RelationshipNotFound(relname)
    elif relationship.to_one:
        relative = relationship.get(resource)
        relatives = [relative] if relative else []
    else:
        relatives = relationship.get(resource)

    relatives = [
        ensure_identifier(api, relative) for relative in relatives
    ]
    return None


def replace_identifiers_in_jsonapi_object(relobj, resources):
    """
    .. todo::

        Find a better name for this function.

    Takes a JSONapi relationship object *relobj* and tries to replace each
    identifier object ``{"id": ..., "type": ...}`` with a resource in
    *resources*.

    .. code-block:: python3

        >>> relobj
        {
            "author": {
                "data": {"type": "User", "id": 42}
            },
            "comments": {
                "data": [
                    {"type": "User", "id": "19"},
                    {"type": "User", "id": "20"}
                ]
            }
            "publisher": {
                "data": None
        }
        >>> relative_ids = collect_identifiers(relobj)
        >>> relatives = db.get_many(relative_ids)
        >>> relatives = replace_identifiers_in_jsonapi_object(relobj, relatives)
        >>> relatives
        {
            "author": UserObject(...),
            "comments": [UserObject(...), UserObject(...)],
            "publisher": None
        }

    :arg dict relobj:
        A JSONapi relationships document.
    :arg dict resources:
        A dictionary, containing all resources with an id in the relationships
        document.
    """
    result = dict()
    for relname in reldoc.keys():
        # Skip the relationship, if the *data* dictionary is not present.
        if not "data" in reldoc[relname]:
            continue

        reldata = reldoc[relname]["data"]
        if reldata is None:
            result[relname] = None
        elif isinstance(reldata, dict):
            result[relname] = resources[(reldata["type"], reldata["id"])]
        elif isinstance(reldata, list):
            result[relname] = [
                resources[(item["type"], item["id"])] for item in reldata
            ]
    return result
