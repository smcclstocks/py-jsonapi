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
    api = jsonapi.flask.FlaskAPI("/api", db=..., flask_app=app)

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

# local
from .api import FlaskAPI, current_api
