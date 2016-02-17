#!/usr/bin/env python3

"""
jsonapi.asyncio.api
===================

:license: GNU Affero General Public License v3

API base application for asynchronous web frameworks.
"""

# std
import asyncio
import re
import logging

# local
import jsonapi
from jsonapi.base import errors
from . import handler
from . import serializer


__all__ = [
    "API"
]


LOG = logging.getLogger(__file__)


class API(jsonapi.base.api.API):
    """
    Overrides the base API to support asynchronous web frameworks.
    """

    def _create_routes(self):
        """
        The same as the base class method, but uses our asynchronous handlers.
        """
        base_url = self._uri.rstrip("/")

        collection = base_url + "/(?P<type>[A-z][A-z0-9]*)"
        resource = collection + "/(?P<id>[A-z0-9]+)"
        relationships = resource + "/relationships/(?P<relname>[A-z][A-z0-9]*)"
        related = resource + "/(?P<relname>[A-z][A-z0-9]*)"

        # Make the rules insensitive against a trailing "/"
        collection = re.compile(collection + "/?")
        resource = re.compile(resource + "/?")
        relationships = re.compile(relationships + "/?")
        related = re.compile(related + "/?")

        # Add the routes.
        self._routes.extend([
            (collection, handler.CollectionHandler),
            (resource, handler.ResourceHandler),
            (relationships, handler.RelationshipHandler),
            (related, handler.RelatedHandler)
        ])
        return None

    def add_type(self, schema):
        """
        """
        super().add_type(schema)

        unserializer = serializer.Unserializer(schema)
        self._unserializers[schema.typename] = unserializer
        schema.resource_class._jsonapi["unserializer"] = unserializer
        return None

    async def handle_request(self, request):
        """
        """
        assert request.api is None or request.api is self
        request.api = self

        try:
            HandlerType = self._find_handler(request)
            handler = HandlerType(
                api=self, db=self._db.session(), request=request
            )

            if asyncio.iscoroutinefunction(handler.prepare):
                await handler.prepare()
            else:
                handler.prepare()

            await handler.handle()
        except (errors.Error, errors.ErrorList) as err:
            LOG.debug(err, exc_info=False)
            if not self.debug:
                return errors.error_to_response(err, self.dump_json)
            else:
                raise
        except Exception as err:
            LOG.critical(err, exc_info=True)
            raise
        else:
            return handler.response
