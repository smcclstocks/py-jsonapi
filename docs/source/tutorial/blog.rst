Blog
====

.. seealso::

    You can find the blog application in the
    `examples folder <https://github.com/benediktschmitt/py-jsonapi/tree/master/examples/blog>`_.

Our little blog has only three models: *User*, *Post* and *Comment*. It's a
simple *sqlalchemy* powered *flask* application with no front-end.

.. literalinclude:: ../../../examples/blog/app.py
    :lines: 1-2, 8-
    :emphasize-lines: 76-90, 99-100

If you run the script, the resources will be available at:

.. code-block:: none

    localhost:5000/api/User
    localhost:5000/api/Post
    localhost:5000/api/Comment
