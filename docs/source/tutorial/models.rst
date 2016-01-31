Models
======

First of all, we need to define the models for our database. For our blog,
we need a *User*, *Post* and *Comment* schema.

You can use special decorators to tell the serializer about attributes and
relationships, which are no sqlalchemy columns.

:file:`db.py`
-------------

First of all, let us define the sqlalchemy engine and base in the :file:`db.py`
module, which contains the settings for our database connection:

.. literalinclude:: ../../../examples/blog/db.py
    :linenos:

:file:`models.py`
-----------------

Now we define our three models in the :file:`models.py` file.

User
~~~~

The user model is implemented straightforward.

.. literalinclude:: ../../../examples/blog/models.py
    :linenos:
    :pyobject: User

.. literalinclude:: ../../../examples/blog/models.py
    :linenos:
    :pyobject: Post

.. literalinclude:: ../../../examples/blog/models.py
    :linenos:
    :pyobject: Comment
