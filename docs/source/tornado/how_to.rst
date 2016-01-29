How to
======

It's as simple as:

.. code-block:: python3

    #!/usr/bin/env python3

    import tornado
    import tornado.web

    import jsonapi
    import jsonapi.tornado

    app = tornado.web.Application()
    api = jsonapi.tornado.TornadoAPI("/api", tornado_app=app)

    # If the tornado application is not available, when you construct the API,
    # you can initialize it later:
    #api.init_app(app)

The :class:`~jsonapi.base.api.API` is added to the *app's* *settings*
dictionary:

.. code-block:: python3

    app.settings["jsonapi"]
