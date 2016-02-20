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
jsonapi.asyncio.database
========================

Defines the interface for an asynchronous database adapters.
"""

# std
import asyncio

# local
import jsonapi
from jsonapi.base import errors
from jsonapi.base.utilities import relative_identifiers


__all__ = [
    "Database",
    "Session"
]


class Database(jsonapi.base.database.Database):
    """
    The same as the base database class, but you should inherit from this
    class, because we may extend it in the future.
    """


class Session(jsonapi.base.database.Session):
    """
    The same as :class:`jsonapi.base.database.Session`, but some methods must
    return *awaitables*:

    *   :meth:`query`
    *   :meth:`query_size`
    *   :meth:`get`
    *   :meth:`get_many`
    *   :meth:`commit`
    *   :meth:`get_relatives`
    """

    @asyncio.coroutine
    def get_relatives(self, resources, paths):
        """
        **May be overridden** for performance reasons.

        Does the same as :meth:`jsonapi.base.database.Session.get_relatives`,
        but asynchronous.

        .. todo::

            Fetch the different paths in *paths* parallel.
        """
        all_relatives = dict()
        root_resources = resources

        for path in paths:
            resources = root_resources
            for relname in path:
                # Collect the ids of all related resources.
                relids = set()
                for resource in resources:
                    try:
                        tmp = relative_identifiers(relname, resource)
                    except errors.RelationshipNotFound:
                        raise errors.UnresolvableIncludePath(path)
                    else:
                        relids.update(tmp)

                # Query the relatives from the database.
                relatives = yield from self.get_many(relids, required=True)
                all_relatives.update(relatives)

                # The next relationship name in the path is defined on the
                # previously fetched relatives.
                resources = relatives.values()
        return all_relatives
