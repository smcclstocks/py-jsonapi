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
jsonapi.base.validators
=======================

This module contains validators for the different JSONapi document types. If a
request contains an invalid document, a validator detects the error source and
creates a verbose error with a *source-pointer*.

All validators only assert the correct document structure, e.g.: An identifier
document must contain an *id* and a *type* attribute. However, the validator
does not check if the *type* and *id* exists.

.. seealso::

    *   http://jsonapi.org/format/#document-structure
    *   http://jsonapi.org/format/#errors
"""

# local
from . import errors


__all__ = [
    "assert_resource_document",
    "assert_attributes_document",
    "assert_relationships_document",
    "assert_relationship_document",
    "assert_identifier_document",
    "assert_links_document",
    "assert_link_document",
    "assert_meta_document"
]


def assert_resource_document(d, source_pointer="/"):
    """
    Returns True, if *d* is a resource object.

    :seealso: http://jsonapi.org/format/#document-resource-objects

    :arg d:
    :arg str source_pointer:

    :raises jsonapi.base.errors.InvalidDocument:
    """
    if not isinstance(d, dict):
        raise errors.InvalidDocument(
            detail="A resource document must be an object (dict).",
            source_pointer=source_pointer
        )
    if "attributes" in d:
        assert_attributes_document(
            d["attributes"], source_pointer + "attributes/"
        )
    if "relationships" in d:
        assert_relationships_document(
            d["relationships"], source_pointer + "relationships/"
        )
    if "links" in d:
        assert_links_document(
            d["links"], source_pointer + "links/"
        )
    if "meta" in d:
        assert_meta_document(
            d["meta"], source_pointer + "meta/"
        )
    return None


def assert_attributes_document(d, source_pointer="/"):
    """
    Returns True, if *d* is an attribute document.

    :arg d:
    :arg str source_pointer:

    :raises jsonapi.base.errors.InvalidDocument:
    """
    if not isinstance(d, dict):
        raise errors.InvalidDocument(
            detail="An attributes document must be an object.",
            source_pointer=source_pointer
        )
    return None


def assert_relationships_document(d, source_pointer="/"):
    """
    Returns True, if *d* is a relationships object.

    :seealso: http://jsonapi.org/format/#document-resource-object-relationships

    :arg d:
    :arg str source_pointer:

    :raises jsonapi.base.errors.InvalidDocument:
    """
    if not isinstance(d, dict):
        raise errors.InvalidDocument(
            detail="A relationships document must be an object.",
            source_pointer=source_pointer
        )
    for relname, relvalue in d.items():
        assert_relationship_document(relvalue, source_pointer + relname + "/")
    return None


def assert_relationship_document(d, source_pointer="/"):
    """
    Returns True, if *d* is a relationship object.

    :seelso: http://jsonapi.org/format/#document-resource-object-relationships

    :arg d:
    :arg str source_pointer:

    :raises jsonapi.base.errors.InvalidDocument:
    """
    if not isinstance(d, dict):
        raise errors.InvalidDocument(
            detail="A relationship document must be an object",
            source_pointer=source_pointer
        )
    if "links" in d:
        assert_links_document(d["links"], source_pointer + "links/")
    if "meta" in d:
        assert_meta_document(d["meta"], source_pointer + "meta/")
    if "data" in d:
        data = d["data"]

        # *to-one* relationship with not id
        if data is None:
            pass

        # *to-one* relationship with id
        elif isinstance(data, dict):
            assert_identifier_document(data, source_pointer + "data/")

        # *to-many* relationship
        elif isinstance(data, list):
            for i, item in enumerate(data):
                assert_identifier_document(
                    item, source_pointer + "data[" + str(i) + "]/"
                )
    return None


def assert_identifier_document(d, source_pointer="/"):
    """
    Returns True, if *d* is an identifier object.

    :seealso: http://jsonapi.org/format/#document-resource-identifier-objects

    :arg d:
    :arg str source_pointer:

    :raises jsonapi.base.errors.InvalidDocument:
    """
    if "meta" in d:
        self.assert_meta_document(d["meta"], source_pointer + "meta/")

    if not "type" in d:
        raise errors.InvalidDocument(
            detail="The 'type' field is not present.",
            source_pointer=source_pointer
        )
    if not isinstance(d["type"], str):
        raise errors.InvalidDocument(
            detail="The 'type' value must be a string.",
            source_pointer=source_pointer
        )

    if not "id" in d:
        raise errors.InvalidDocument(
            detail="The 'id' field is not present.",
            source_pointer=source_pointer
        )
    if not isinstance(d["id"], str):
        raise errors.InvalidDocument(
            detail="The 'id' value must be a string.",
            source_pointer=source_pointer
        )
    return None


def assert_links_document(d, source_pointer="/"):
    """
    Returns True, if *d* is a dictionary and all values in *d* are link
    documents.

    :seealso: http://jsonapi.org/format/#document-links

    :arg d:
    :arg str source_pointer:

    :raises jsonapi.base.errors.InvalidDocument:
    """
    if not isinstance(d, dict):
        raise errors.InvalidDocument(
            detail="A links document must be an object.",
            source_pointer=source_pointer
        )

    for linkname, linkvalue in d.items():
        assert_link_document(linkvalue, source_pointer + linkname + "/")
    return None


def assert_link_document(d, source_pointer="/"):
    """
    Returns True, if *d* is a link object. If *d* is a dictionary, we assume
    that *href* and *meta* are both present.

    :seealso: http://jsonapi.org/format/#document-links

    :arg d:
    :arg str source_pointer:

    :raises jsonapi.base.errors.InvalidDocument:
    """
    if not isinstance(d, (str, dict)):
        raise errors.InvalidDocument(
            detail="A link document must be a string or an object.",
            source_pointer=source_pointer
        )

    if isinstance(d, dict):
        if not ("href" in d and isinstance(d["href"], str)):
            raise errors.InvalidDocument(
                detail="The 'href' value must be a string.",
                source_pointer=source_pointer + "href/"
            )
        if "meta" in d:
            assert_meta_document(d["meta"], source_pointer + "meta/")
    return None


def assert_meta_document(d, source_pointer="/"):
    """
    Returns True, if *d* is a meta object. This is the case, if *d* is a
    dictionary.

    :seealso: http://jsonapi.org/format/#document-meta

    :arg d:
    :arg str source_pointer:

    :raises jsonapi.base.errors.InvalidDocument:
    """
    if not isinstance(d, dict):
        raise errors.InvalidDocument(
            detail="A meta document must be an object.",
            source_pointer=source_pointer
        )
    return None
