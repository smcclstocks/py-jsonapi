Welcome to py-jsonapi's documentation!
======================================

.. toctree::
    :maxdepth: 1

    tutorial/index
    base
    marker

.. toctree::
    :maxdepth: 1
    :caption: Database drivers

    mongoengine
    sqlalchemy

.. toctree::
    :maxdepth: 1
    :caption: Web frameworks

    flask
    tornado

.. toctree::
    :maxdepth: 1
    :caption: About py-jsonapi

    contribute
    license
    about

Indices and tables
------------------

*   :ref:`genindex`
*   :ref:`modindex`
*   :ref:`search`

Description
-----------

This library implements the http://jsonapi.org specification in **Python 3**.
It is easy to use, extendible and comes with support for many web frameworks and
database drivers, like :mod:`~jsonapi.flask`, :mod:`~jsonapi.tornado`,
:mod:`~jsonapi.mongoengine` and :mod:`~jsonapi.sqlalchemy`.

Here is a simple API using *flask* and *mongoengine*, in only 5 lines:

.. literalinclude:: ../../examples/teaser.py
    :linenos:
    :emphasize-lines: 8,15-17
