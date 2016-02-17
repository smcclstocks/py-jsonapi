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
jsonapi.base.validators
=======================

This module contains validators for the different JSONapi document types. If a
request contains an invalid document, a validator detects the error source and
creates a verbose error with a *source-pointer*.

All validators only assert the correct document structure, e.g.: An identifier
object must contain an *id* and a *type* attribute. However, the validator
does not check, if the type is correct.

.. seealso::

    *   http://jsonapi.org/format/#document-structure
    *   http://jsonapi.org/format/#errors
"""

# local
from .errors import InvalidDocument


__all__ = [
    "assert_resource_object",
    "assert_attributes_object",
    "assert_relationships_object",
    "assert_relationship_object",
    "assert_resource_linkage",
    "assert_resource_identifier_object",
    "assert_links_object",
    "assert_link_object",
    "assert_meta_object"
]


def assert_resource_object(d, source_pointer="/"):
    """
    Asserts, that *d* is a JSONapi resource object.

    :seealso: http://jsonapi.org/format/#document-resource-objects

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if not isinstance(d, dict):
        raise InvalidDocument(
            detail="A resource object must be an object.",
            source_pointer=source_pointer
        )

    if not d.keys() <= {"id", "type", "attributes", "relationships", "links", "meta"}:
        raise InvalidDocument(
            detail=(
                "A resource object may only contain these members: "\
                "'id', 'type', 'attributes', 'relationships', 'links', 'meta'."
            ),
            source_pointer=source_pointer
        )

    if not "type" in d:
        raise InvalidDocument(
            detail="The 'type' member is not present.",
            source_pointer=source_pointer
        )
    if not isinstance(d["type"], str):
        raise InvalidDocument(
            detail="The value of 'type' must be a string.",
            source_pointer=source_pointer + "type/"
        )

    if "id" in d and not isinstance(d["id"], str):
        raise InvalidDocument(
            detail="The value 'id' must be a string.",
            source_pointer=source_pointer + "id/"
        )

    if "attributes" in d:
        assert_attributes_object(
            d["attributes"], source_pointer + "attributes/"
        )
    if "relationships" in d:
        assert_relationships_object(
            d["relationships"], source_pointer + "relationships/"
        )
    if "links" in d:
        assert_links_object(
            d["links"], source_pointer + "links/"
        )
    if "meta" in d:
        assert_meta_object(
            d["meta"], source_pointer + "meta/"
        )
    return None


def assert_attributes_object(d, source_pointer="/"):
    """
    Asserts, that *d* is a JSONapi attributes object.

    :seealso: http://jsonapi.org/format/#document-resource-object-attributes

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if not isinstance(d, dict):
        raise InvalidDocument(
            detail="An attributes object must be an object.",
            source_pointer=source_pointer
        )
    return None


def assert_relationships_object(d, source_pointer="/"):
    """
    Asserts, that *d* is a JSONapi relationships object.

    :seealso: http://jsonapi.org/format/#document-resource-object-relationships

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if not isinstance(d, dict):
        raise InvalidDocument(
            detail="A relationships object must be an object.",
            source_pointer=source_pointer
        )

    for key, value in d.items():
        assert_relationship_object(value, source_pointer + key + "/")
    return None


def assert_relationship_object(d, source_pointer="/"):
    """
    Asserts, that *d* is a relationship object.

    :seelso: http://jsonapi.org/format/#document-resource-object-relationships

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if not isinstance(d, dict):
        raise InvalidDocument(
            detail="A relationship object must be an object",
            source_pointer=source_pointer
        )
    if not d:
        raise InvalidDocument(
            detail=(
                "A relationship object must contain at least one of these "
                "members: 'data', 'links', 'meta'."
            ),
            source_pointer=source_pointer
        )
    if not d.keys() <= {"links", "data", "meta"}:
        raise InvalidDocument(
            detail=(
                "A relationship object may only contain the following members: "
                "'links', 'data' and 'meta'."
            ),
            source_pointer=source_pointer
        )

    if "links" in d:
        assert_links_object(d["links"], source_pointer + "links/")
    if "meta" in d:
        assert_meta_object(d["meta"], source_pointer + "meta/")
    if "data" in d:
        assert_resource_linkage(d["data"], source_pointer + "data/")
    return None


def assert_resource_linkage(d, source_pointer="/"):
    """
    Asserts, that *d* is a resource linkage.

    :seealso: http://jsonapi.org/format/#document-resource-object-linkage

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if d is None:
        # Nothing to do here.
        pass
    elif isinstance(d, dict):
        assert_resource_identifier_object(d, source_pointer)
    elif isinstance(d, list):
        for i, item in enumerate(d):
            assert_resource_identifier_object(
                item, source_pointer + str(i) + "/"
            )
    else:
        raise InvalidDocument(
            detail=(
                "A resource linkage must be 'None', '[]', a resource "
                "identifier object or an array of resource identifier objects."
            ),
            source_pointer=source_pointer
        )
    return None


def assert_resource_identifier_object(d, source_pointer="/"):
    """
    Asserts, that *d* is a resource identifier object.

    :seealso: http://jsonapi.org/format/#document-resource-identifier-objects

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if not isinstance(d, dict):
        raise InvalidDocument(
            detail="A resource identifier object must be an object.",
            source_pointer=source_pointer
        )
    if not d.keys() <= {"id", "type", "meta"}:
        raise InvalidDocument(
            detail=(
                "A resource identifier object can only contain these members: "
                "'id', 'type', 'meta'."
            ),
            source_pointer=source_pointer
        )

    if "meta" in d:
        self.assert_meta_object(d["meta"], source_pointer + "meta/")

    if not "type" in d:
        raise InvalidDocument(
            detail="The 'type' member is not present.",
            source_pointer=source_pointer
        )
    if not isinstance(d["type"], str):
        raise InvalidDocument(
            detail="The value of 'type' must be a string.",
            source_pointer=source_pointer + "type/"
        )

    if not "id" in d:
        raise InvalidDocument(
            detail="The 'id' member is not present.",
            source_pointer=source_pointer
        )
    if not isinstance(d["id"], str):
        raise InvalidDocument(
            detail="The value of 'id' must be a string.",
            source_pointer=source_pointer + "id/"
        )
    return None


def assert_links_object(d, source_pointer="/"):
    """
    Asserts, that *d* is a JSONapi links object.

    :seealso: http://jsonapi.org/format/#document-links

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if not isinstance(d, dict):
        raise InvalidDocument(
            detail="A links object must be an object.",
            source_pointer=source_pointer
        )

    for key, value in d.items():
        assert_link_object(value, source_pointer + key + "/")
    return None


def assert_link_object(d, source_pointer="/"):
    """
    Asserts, that *d* is a JSONapi link object.

    :seealso: http://jsonapi.org/format/#document-links

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if isinstance(d, str):
        pass
    elif isinstance(d, dict):
        if not d.keys() <= {"href", "meta"}:
            raise InvalidDocument(
                detail=(
                    "A link object can only contain these members: "
                    "'href', 'meta'."
                ),
                source_pointer=source_pointer
            )
        if "href" in d and not isinstance(d["href"], str):
            raise InvalidDocument(
                detail="The value of 'href' must be a string.",
                source_pointer=source_pointer + "href/"
            )
        if "meta" in d:
            assert_meta_object(d["meta"], source_pointer + "meta/")
    else:
        raise InvalidDocument(
            detail="A link object must be a string or an object.",
            source_pointer=source_pointer
        )
    return None


def assert_meta_object(d, source_pointer="/"):
    """
    Asserts that *d* is a meta object.

    :seealso: http://jsonapi.org/format/#document-meta

    :arg d:
    :arg str source_pointer:

    :raises InvalidDocument:
    """
    if not isinstance(d, dict):
        raise InvalidDocument(
            detail="A meta object must be an object.",
            source_pointer=source_pointer
        )
    return None
