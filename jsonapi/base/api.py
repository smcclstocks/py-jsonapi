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
jsonapi.base.api
================

The API application. It handles all requests and knows all available resource
types.
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
from . import serializer


__all__ = [
    "build_uris",
    "API"
]


LOG = logging.getLogger(__file__)


ARG_DEFAULT = []


def build_uris(base_uri):
    """
    Returns a dictionary with the uri re(s) for each endpoint type (collection,
    resource, related and relationships).

    :arg str base_uri:
    """
    base_url = base_uri.rstrip("/")

    collection = base_url + "/(?P<type>[A-z][A-z0-9]*)"
    resource = collection + "/(?P<id>[A-z0-9]+)"
    relationships = resource + "/relationships/(?P<relname>[A-z][A-z0-9]*)"
    related = resource + "/(?P<relname>[A-z][A-z0-9]*)"

    # Make the rules insensitive against a trailing "/"
    collection = re.compile(collection + "/?")
    resource = re.compile(resource + "/?")
    relationships = re.compile(relationships + "/?")
    related = re.compile(related + "/?")

    return {
        "collection": collection, "resource": resource,
        "relationships": relationships, "related": related
    }


class API(object):
    """
    This class is responsible for the request dispatching. It knows all
    resource classes, typenames, serializers and database adapter.

    :arg str uri:
        The root uri of the whole API.
    :arg jsonapi.base.database.Database db:
        The database adapter we use to load resources
    :arg bool debug:
        If true, exceptions are not catched and the API is more verbose.
    :arg dict settings:
        A dictionary containing settings, which may be used by extensions.
    """

    def __init__(self, uri, db, debug=False, settings=None):
        """
        """
        # True, if in debug mode.
        self._debug = debug

        self._uri = uri.rstrip("/")
        self._parsed_uri = urllib.parse.urlparse(self.uri)

        # List of tuples: `(uri_regex, handler_type)`
        self._routes = list()
        self._create_routes()

        #: A dictionary, containing settings for extensions, the handlers, ...
        self.settings = settings or dict()
        assert isinstance(self.settings, dict)

        # resource class to typename
        self._typenames = dict()

        # typename to ...
        self._schemas = dict()
        self._resource_classes = dict()
        self._serializers = dict()
        self._unserializers = dict()

        # The database adapter we use to load, save and delete resources.
        self._db = db
        db.init_api(self)

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

        This value **can be overridden** in subclasses to mimic the behaviour of
        the parent web framework.
        """
        return self._debug

    @property
    def database(self):
        """
        :rtype: jsonapi.base.database.Database
        :returns:
            The database the API uses to load, save and delete resources.
        """
        return self._db

    def _create_routes(self):
        """
        Builds the regular expressions, which match the different endpoint
        types (collection, resource, related, relationships, ...) and adds
        them to :attr:`_routes`.

        You may **override** this method, if you want to use other handlers
        in your API.
        """
        uris = build_uris(self._uri)
        self._routes.extend([
            (uris["collection"], handler.CollectionHandler),
            (uris["related"], handler.RelatedHandler),
            (uris["resource"], handler.ResourceHandler),
            (uris["relationships"], handler.RelationshipHandler)
        ])
        return None


    def get_resource_class(self, typename, default=ARG_DEFAULT):
        """
        Returns the resource class associated with the *typename*.

        :arg str typename:
            The typename of the resource class
        :arg default:
            A fallback value, if the typename does not exist.
        :raises KeyError:
            If the typename does not exist and no default argument is given.
        """
        if default is ARG_DEFAULT:
            return self._resource_classes[typename]
        else:
            return self._resource_classes.get(typename, default)

    def get_schema(self, typename, default=ARG_DEFAULT):
        """
        Returns the JSONapi schema which represents the structure of the
        resource type with the given typename.

        :arg str typename:
        :arg default:
            A fallback value, if the typename does not exist.
        :raises KeyError:
            If the typename is not associated with a schema and no default
            argument is given.
        :rtype: jsonapi.base.schema.Schema
        """
        if default is ARG_DEFAULT:
            return self._schemas[typename]
        else:
            return self._schemas.get(typename, default)

    def get_serializer(self, typename, default=ARG_DEFAULT):
        """
        Returns the serializer used to serialize types of *typename*.

        :arg str typename:
        :arg default:
            A fallback value, if the typename does not exist.
        :raises KeyError:
            If the typename does not exist and no default argument is given.
        """
        if default is ARG_DEFAULT:
            return self._serializers[typename]
        else:
            return self._serializers.get(typename, default)

    def get_unserializer(self, typename, default=ARG_DEFAULT):
        """
        Returns the unserializer used to unserialize types of *typename*.

        :arg str typename:
        :arg default:
            A fallback value, if the typename does not exist.
        :raises KeyError:
            If the typename does not exist and no default argument is given.
        """
        if default is ARG_DEFAULT:
            return self._unserializers[typename]
        else:
            return self._unserializers.get(typename, default)

    def get_typename(self, o, default=ARG_DEFAULT):
        """
        Returns the typename of the object *o*.

        :arg o:
            A resource class or a resource
        :arg default:
            A fallback value, if the typename can not be retrieved.
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

    def has_type(self, typename):
        """
        Returns True, if the api has a type with the given name and False
        otherwise.

        :arg str typename:
        """
        return typename in self._schemas


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

    def add_type(self, schema, **kargs):
        """
        Adds the serializer to the API.

        :arg jsonapi.base.schema.Schema schema:
        """
        serializer_ = kargs.get("serializer") or serializer.Serializer(schema)
        unserializer = kargs.get("unserializer") or serializer.Unserializer(schema)
        resource_class = schema.resource_class

        self._typenames[schema.resource_class] = schema.typename
        self._schemas[schema.typename] = schema
        self._resource_classes[schema.typename] = resource_class
        self._serializers[schema.typename] = serializer_
        self._unserializers[schema.typename] = unserializer

        # Add some new keys to the _jsonapi attribute of the resource class.
        resource_class._jsonapi = getattr(resource_class, "_jsonapi", dict())
        resource_class._jsonapi.update({
            "typename": schema.typename,
            "schema": schema,
            "serializer": serializer_,
            "unserializer": unserializer,
            "api": self
        })
        return None

    def _find_handler(self, request):
        """
        Parses the :attr:`request.uri` and returns the handler for the requested
        endpoint.

        Arguments decoded in the uri (like the resource id or relationship name)
        are saved in :attr:`request.japi_uri_arguments`.

        :arg jsonapi.base.request.Request request:
        :rtype: jsonapi.base.handler.base_handler.BaseHandler:
        :raises jsonapi.base.errors.NotFound:
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
        assert request.api is None or request.api is self
        request.api = self

        try:
            HandlerType = self._find_handler(request)
            handler = HandlerType(
                api=self, db=self._db.session(), request=request
            )

            handler.prepare()
            handler.handle()
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
