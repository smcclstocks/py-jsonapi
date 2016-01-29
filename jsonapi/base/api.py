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
jsonapi.base.api
================

This module contains the API class. It dispatches the requests and know all
available resource types. When you want to integrate *py-jsonapi* in a new
web framework, you will have to subclass :class:`API`.
"""

# std
from collections import OrderedDict
import json
import logging
import re
import urllib.parse

# thid party
try:
    import bson
    import bson.json_util
except ImportError:
    bson = None

# local
from .. import version
from . import errors
from . import handler


__all__ = [
    "API"
]


LOG = logging.getLogger(__file__)


ARG_DEFAULT = []


class API(object):
    """
    This class works as container for all resource types, serializers and
    manages the request handling.

    :arg str uri:
        The root uri of the whole API.
    :arg bool debug:
        If true, exceptions are not catched and the API is more verbose.
    :arg dict settings:
        A dictionary containing settings, which may be used by extensions.
    """

    def __init__(self, uri, debug=False, settings=None):
        """
        """
        # True, if in debug mode.
        self._debug = debug

        self._uri = uri.rstrip("/")
        self._parsed_uri = urllib.parse.urlparse(self.uri)

        # List of tuples: `(uri_regex, handler_type)`
        self._routes = list()
        self._create_routes()

        self.settings = settings or dict()
        assert isinstance(self.settings, dict)

        # model (class) to typename
        self._typenames = dict()

        # typename to ...
        self._models = dict()
        self._dbs = dict()
        self._serializers = dict()
        self._markups = dict()

        #: The global jsonapi object, which is added to each response.
        #:
        #: You are free to add meta information in the
        #: ``jsonapi_object["meta"]`` dictionary.
        #:
        #: :seealso: http://jsonapi.org/format/#document-jsonapi-object
        self.jsonapi_object = OrderedDict()
        self.jsonapi_object["version"] = version.jsonapi_version
        self.jsonapi_object["meta"] = OrderedDict()
        self.jsonapi_object["meta"]["py-jsonapi-version"] = version.version
        return None

    @property
    def debug(self):
        """
        True, if the API is in debug mode.

        This value can be overridden in subclasses to mimic the behaviour of
        the parent web framework.
        """
        return self._debug

    def _create_routes(self):
        """
        Builds the regular expressions, which match the different endpoint
        types (collection, resource, related, relationships, ...) and adds
        them to :attr:`_routes`.
        """
        base_url = self._uri.rstrip("/")

        collection = base_url + "/(?P<type>[A-z][A-z0-9]*)"
        resource = collection + "/(?P<id>[A-z0-9]+)"
        relationships = resource + "/relationships/(?P<relname>[A-z][A-z0-9]*)"
        related = resource + "/(?P<relname>[A-z][A-z0-9]*)"

        # Make the rules resistant against a trailing "/"
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


    def get_model(self, typename, default=ARG_DEFAULT):
        """
        Returns the model associated with the *typename*.

        :arg str typename:
            The typename of the model
        :arg default:
            A fallback value, if the typename does not exist.
        :raises KeyError:
            If the typename does not exist and no default argument is given.
        """
        if default is ARG_DEFAULT:
            return self._models[typename]
        else:
            return self._models.get(typename, default)

    def get_db(self, typename, default=ARG_DEFAULT):
        """
        Returns the database used to load and save resources of the type
        *typename*.

        :arg str typename:
        :arg default:
        :raises KeyError:
            If the typename does not exist and no default argument is given.
        """
        if default is ARG_DEFAULT:
            return self._dbs[typename]
        else:
            return self._dbs.get(typename, default)

    def get_markup(self, typename, default=ARG_DEFAULT):
        """
        If the serializer of the type *typename* is based on
        :mod:`~jsonapi.marker`, the :class:`~jsonapi.marker.Markup` is returned.

        :arg str typename:
        :arg default:
        :raises KeyError:
            If the typename is not associated with a markup and no default
            argument is given.
        """
        if default is ARG_DEFAULT:
            return self._markups[typename]
        else:
            return self._markups.get(typename, default)

    def get_serializer(self, typename, default=ARG_DEFAULT):
        """
        Returns the serializer used to serialize types of *typename*.

        :arg str typename:
        :arg default:
        :raises KeyError:
            If the typename does not exist and no default argument is given.
        """
        if default is ARG_DEFAULT:
            return self._serializers[typename]
        else:
            return self._serializers.get(typename, default)

    def get_typename(self, o, default=ARG_DEFAULT):
        """
        Returns the typename of the object *o*.

        :arg o:
            A model (resource class) or a resource
        :arg default:
        :raises KeyError:
            If the resource type of *o* is not known to the API and no default
            argument is given.
        """
        typename = self._typenames.get(o) \
            or self._typenames.get(type(o)) \
            or default

        if typename is ARG_DEFAULT:
            raise KeyError("The type of *o* is not known to the API.")
        return typename

    def get_typenames(self):
        """
        :rtype: list
        :returns:
            A list with all typenames known to the API.
        """
        return list(self._typenames.values())


    def dump_json(self, d):
        """
        Encodes the object *d* as JSON string.

        This method *can be overridden* if you want to use your own json
        serializer.

        The default implementation uses the :mod:`json` module of the standard
        library and (if available) the :mod:`bson` json utils.

        :arg d:
        :rtype: str
        """
        indent = 1 if self.debug else None
        if bson:
            return json.dumps(d, default=bson.json_util.default, indent=indent)
        else:
            return json.dumps(d, indent=indent)

    def load_json(self, s):
        """
        Decods the JSON string *s*.

        This method *can be overridden* if you want to use your own json
        serializer.

        The default implementation uses the :mod:`json` module of the standard
        library and (if available) the :mod:`bson` json utils.

        :arg str s:
        """
        if bson:
            return json.loads(s, object_hook=bson.json_util.object_hook)
        else:
            return json.loads(s)


    @property
    def uri(self):
        """
        The root uri of api, which has been provided in the constructor.
        """
        return self._uri

    def reverse_url(self, typename, endpoint, **kargs):
        """
        Returns the url for the API endpoint for the type with the given
        typename.

        .. code-block:: python

            >>> api.reverse_url("User", "collection")
            "/api/User/"

            >>> api.reverse_url("User", "resource", id="AA-23")
            "/api/User/AA-23"

            >>> api.reverse_url(
            ...     "User", "relationship", id="AA-23", relname="articles"
            ... )
            "/api/User/AA-23/relationships/articles"

            >>> api.reverse_url(
            ...     "User", "related", id="AA-23", relname="articles"
            ... )
            "/api/User/AA-23/articles"

        :arg str typename:
        :arg str endpoint:
            *collection*, *resource*, *related* or *relationship*
        :arg kargs:
            Additional arguments needed to build the uri. For example: The
            resource endpoint also needs the resource's *id*.

        :rtype: str

        :raises ValueError:
            If the endpoint type does not exist.
        :raises ValueError:
            If the typename does not exist.
        """
        if not typename in self._serializers:
            raise ValueError("Unknown typename '{}'".format(typename))

        if endpoint == "collection":
            return "{}/{}".format(self._uri, typename)
        elif endpoint == "resource":
            return "{}/{}/{}".format(self._uri, typename, kargs["id"])
        elif endpoint == "relationship":
            return "{}/{}/{}/relationships/{}".format(
                self._uri, typename, kargs["id"], kargs["relname"]
            )
        elif endpoint == "related":
            return "{}/{}/{}/{}".format(
                self._uri, typename, kargs["id"], kargs["relname"]
            )
        else:
            raise ValueError("Unknown endpoint type '{}'".format(endpoint))

    def add_model(self, serializer, db):
        """
        Adds the serializer to the API.

        :arg jsonapi.base.serializer.Serializer serializer:
        :arg jsonapi.base.database.Database db:
        """
        typename = serializer.typename
        model = serializer.model

        if db.api is None:
            db.init_api(self)
        assert db.api is self

        if serializer.api is None:
            serializer.init_api(self)
        assert serializer.api is self

        self._typenames[model] = typename
        self._models[typename] = model
        self._dbs[typename] = db
        self._serializers[typename] = serializer
        if getattr(serializer, "markup", None) is not None:
            self._markups[typename] = serializer.markup
        return None

    def find_handler(self, request):
        """
        Parses the :attr:`request.uri` and returns the handler for this
        endpoint.

        Arguments decoded in the uri (like the resource id or relationship name)
        are saved in :attr:`request.japi_uri_arguments`.

        :arg jsonapi.base.request.Request request:
        :rtype: jsonapi.base.handler.base_handler.BaseHandler:
        :raises NotFound:
            If the :attr:`request.uri` is not a valid API endpoint.
        """
        for uri_re, HandlerType in self._routes:
            match = uri_re.fullmatch(request.parsed_uri.path)
            if match:
                request.japi_uri_arguments.update(match.groupdict())
                return HandlerType
        raise errors.NotFound()

    def handle_request(self, request):
        """
        Handles the *request* and returns a :class:`Response`.

        :arg jsonapi.base.request.Request request:
        :rtype: jsonapi.base.response.Response
        """
        try:
            HandlerType = self.find_handler(request)
            handler = HandlerType(self, request)

            handler.prepare()
            handler.handle()
        except errors.Error as err:
            LOG.debug(err, exc_info=False)
            if self.debug:
                raise
            else:
                return errors.error_to_response(err, self.dump_json)
        else:
            return handler.response
