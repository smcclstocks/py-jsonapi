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
jsonapi.asyncio.api
===================

API base application for asynchronous web frameworks.
"""

# std
import asyncio
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
        We use our own *asynchronous* handlers. So we have to override this
        method.
        """
        uris = jsonapi.base.api.build_uris(self._uri)
        self._routes.extend([
            (uris["collection"], handler.CollectionHandler),
            (uris["related"], handler.RelatedHandler),
            (uris["resource"], handler.ResourceHandler),
            (uris["relationships"], handler.RelationshipHandler)
        ])
        return None

    def add_type(self, schema, **kargs):
        """
        The same as :meth:`~jsonapi.base.api.API.add_type`, but uses the
        asynchronous :class:`~jsonapi.asyncio.unserializer.Unserializer` as
        default.
        """
        if not "unserializer" in kargs:
            kargs["unserializer"] = serializer.Unserializer(schema)
        super().add_type(schema, **kargs)
        return None

    @asyncio.coroutine
    def handle_request(self, request):
        """
        """
        request.api = self

        try:
            HandlerType = self._find_handler(request)
            handler = HandlerType(
                api=self, db=self._db.session(), request=request
            )

            yield from handler.prepare()
            yield from handler.handle()
        except (errors.Error, errors.ErrorList) as err:
            #LOG.debug(err, exc_info=False)
            print("DEBUG", self.debug)
            print()
            if not self.debug:
                return errors.error_to_response(err, self.dump_json)
            else:
                raise
        except Exception as err:
            LOG.critical(err, exc_info=True)
            raise
        else:
            return handler.response
