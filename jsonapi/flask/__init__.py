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
jsonapi.flask
=============

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
