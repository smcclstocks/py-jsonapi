#!/usr/bin/env python3

"""
jsonapi.asyncio.database
========================

:license: GNU Affero General Public License v3

Defines the interface for an asynchronous database session.
"""

# std
import asnycio

# local
import jsonapi
from jsonapi.base import errors
from jsonapi.base.utilities import relative_identifiers


__all__ = [
    "Session"
]


class Session(jsonapi.base.database.Session):
    """
    The same as :class:`jsonapi.base.database.Session`, but some methods must
    be coroutines.
    """

    async def query(self, typename,
        *, sorting=None, limit=None, offset=None, filters=None
        ):
        """
        **Must be overridden**

        :seealso: :meth:`jsonapi.base.database.Session.query`
        """
        raise NotImplementedError()

    async def query_size(self, typename,
        *, sorting=None, limit=None, offset=None, filters=None
        ):
        """
        **Must be overridden**

        :seealso: :meth:`jsonapi.base.database.Session.query_size`
        """
        raise NotImplementedError()

    async def get(self, identifier, required=False):
        """
        **Must be overridden**

        :seealso: :meth:`jsonapi.base.database.Session.get`
        """
        raise NotImplementedError()

    async def get_many(self, identifiers, required=False):
        """
        **Must be overridden**

        :seealso: :meth:`jsonapi.base.database.Session.get_many`
        """
        raise NotImplementedError()

    async def commit(self):
        """
        **Must be overridden**

        :seealso: :meth:`jsonapi.base.database.Session.commit`
        """
        raise NotImplementedError()

    async def get_relatives(self, resources, paths):
        """
        **May be overridden** for performance reasons.

        :seealso: :meth:`jsonapi.base.database.Session.get_relatives`
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
                relatives = await self.get_many(relids, required=True)
                all_relatives.update(relatives)

                # The next relationship name in the path is defined on the
                # previously fetched relatives.
                resources = relatives.values()
        return all_relatives
