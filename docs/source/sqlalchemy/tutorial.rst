Tutorial
========

If you have a sqlalchemy model, simply use the sqlalchemy serializer. It will
find all sqlalchemy attributes and relationships automatic:

.. code-block:: python3

    serializer = jsonapi.sqlalchemy.Serializer(MyModel)

However, here is a short example:

.. literalinclude:: ../../../examples/sqlalchemy/example.py
    :linenos:
    :emphasize-lines: 4, 48, 50-51, 53-54

sessionmaker
------------

The database adapter needs a sessionmaker to work. There are two ways to
provide a function, that returns a session.

The first one provides the function as init argument for the database adapter:

.. code-block:: python3

    sql_db = jsonapi.sqlalchemy.Database(sessionmaker=get_session)

The other way uses the settings dictionary of the api:

.. code-block:: python3

    api.settings["sqlalchemy_sessionmaker"] = get_session
