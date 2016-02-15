#!/usr/bin/env python3

"""
jsonapi.tornado
===============

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

The *py-jsonapi* extension for tornado. Binding the API to a tornado application
is as simple as:

.. code-block:: python3

    import tornado
    import tornado.web
    import jsonapi
    import jsonapi.tornado

    app = tornado.web.Application()
    api = jsonapi.tornado.TornadoAPI("/api", db=..., tornado_app=app)

    # If the tornado application is not available, when you create the API,
    # you can bind it later:
    api.init_app(app)

The API instance is added to the tornado application's settings dictionary:

.. code-block:: python3

    assert app.settings["jsonapi"] is api

API
---

.. autoclass:: TornadoAPI
"""

# local
from .api import TornadoAPI
