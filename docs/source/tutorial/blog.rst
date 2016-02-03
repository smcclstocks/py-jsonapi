Blog
====

.. seealso::

    You can find the blog application in the
    `examples folder <https://github.com/benediktschmitt/py-jsonapi/tree/master/examples/blog>`_.

Our little blog has only three models: *User*, *Post* and *Comment*. It's a
simple *sqlalchemy* powered *flask* application with no front-end.

.. literalinclude:: ../../../examples/blog/app.py
    :lines: 1-2, 8-
    :emphasize-lines: 76-91, 100-101

The models are served under:

.. code-block:: none

    /api/User
    /api/Post
    /api/Comment
