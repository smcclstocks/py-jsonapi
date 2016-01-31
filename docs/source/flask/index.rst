Flask
=====

Tutorial
--------

The *py-jsonapi* flask extension can be registered on a flask application
like any other extension:

.. code-block:: python3

    #!/usr/bin/env python3

    import flask
    import jsonapi
    import jsonapi.flask

    app = flask.Flask(__name__)
    api = jsonapi.flask.FlaskAPI(uri="/api/", flask_app=app)

    # If the flask application is not available, when you construct the api,
    # you can initialize it later:
    api.init_app(app)

That's it. All models registered on the API are now available under the
the ``/api/`` path.

current_api
~~~~~~~~~~~

You can access the :class:`~jsonapi.base.api.API` via the *extensions*
dictionary of the flask application:

.. code-block:: python3

    app.extensions["jsonapi"]

Or you use the global variable :attr:`~jsonapi.flask.current_api`:

.. code-block:: python3

    from jsonapi.flask import current_api

The *jsonapi* is also added to the *jinja* environment of the application:

.. code-block:: html

    <p>
        You can download your profile
        <a href="{{ jsonapi.reverse_url('User', 'resource', id=current_user.id) }}">
            here
        </a>
    </p>

:mod:`jsonapi.flask`
--------------------

.. automodule:: jsonapi.flask
