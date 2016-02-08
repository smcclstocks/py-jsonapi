#!/usr/bin/env python3

"""
jsonapi.flask
=============

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

The *py-jsonapi* extension for flask. Binding the API to a flask application
is dead simple:

.. code-block:: python3

    import flask
    import jsonapi
    import jsonapi.flask

    app = flask.Flask(__name__)
    api = jsonapi.flask.FlaskAPI("/api", flask_app=app)

    # You can also initialize the API with the flask application using the
    # *init_app()* method:
    api.init_app(app)

You can add the models to the API as usual. They will be available under
``/api``.

current_api
-----------

You can access the current APi via the *extensions* dictionary of the flask
application:

.. code-block:: python3

    app.extensions["jsonapi"]

or you use the global variable ``current_api``:

.. code-block:: python3

    from jsonapi.flask import current_api

The API instance is also added to the jinja environment:

.. code-block:: html

    <p>
        You can download your profile
        <a href="{{ jsonapi.reverse_url('User', 'resource', id=current_user.id) }}">
            here
        </a>
    </p>

API
---

.. autoclass:: FlaskAPI    
.. autodata:: current_api
"""

# std
import logging

# third party
import flask
import werkzeug

# local
import jsonapi


__all__ = [
    "FlaskAPI",
    "current_api"
]


LOG = logging.getLogger(__file__)


def get_request():
    """
    Transforms the current flask request object in to a jsonapi request object.
    """
    uri = flask.request.base_url
    if flask.request.query_string:
        uri += "?" + flask.request.query_string.decode("utf-8")

    method = flask.request.method
    headers = dict(flask.request.headers)
    body = flask.request.get_data()
    return jsonapi.base.Request(uri, method, headers, body)


def to_response(japi_response):
    """
    Transforms the jsonapi response object into a flask response.
    """
    if japi_response.is_file:
        flask_response = flask.send_file(japi_response.file)
    elif japi_response.has_body:
        flask_response = flask.Response(japi_response.body)
    else:
        flask_response = flask.Response("")

    for key, value in japi_response.headers.items():
        flask_response.headers[str(key)] = value
    flask_response.status_code = japi_response.status
    return flask_response


class FlaskAPI(jsonapi.base.api.API):
    """
    Implements the API for flask. You can provide the flask application
    later via :meth:`init_app`.
    """

    def __init__(self, uri, settings=None, flask_app=None):
        """
        """
        super().__init__(uri=uri, settings=settings)

        self._flask_app = None
        if flask_app is not None:
            self.init_app(flask_app)
        return None

    @property
    def debug(self):
        """
        This is a proxy for the :attr:`flask_app` *debug* attribute. This means,
        that you must enable the debug mode on the flask application.
        """
        return self._flask_app.debug

    @property
    def flask_app(self):
        """
        The flask application, this API is registered on.
        """
        return self._flask_app

    def init_app(self, app):
        """
        Registers this API on the flask application *app*.

        :arg flask.Flask app:
        """
        # Avoid double initialization.
        if self._flask_app is app:
            return None
        if self._flask_app is not None:
            raise RuntimeError(
                "This api has already been registered on a flask application."
            )

        self._flask_app = app
        app.extensions = getattr(app, "extensions", dict())
        app.extensions["jsonapi"] = self

        # Add the url rule.
        app.add_url_rule(
            rule=self._uri + "/<path:path>",
            endpoint="jsonapi",
            view_func=self.handle_request,
            methods=["get", "post", "patch", "delete", "head"]
        )

        # Add the api to the jinja environment
        app.jinja_env.globals["jsonapi"] = current_api
        return None

    def handle_request(self, path=None):
        """
        Handles a request to the API.
        """
        req = get_request()
        resp = super().handle_request(req)
        return to_response(resp)


#: Returns the FlaskAPI instance, which is by used by the current flask
#: application.
current_api = werkzeug.local.LocalProxy(
    lambda: flask.current_app.extensions["jsonapi"]
)
