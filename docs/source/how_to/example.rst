Example
=======

.. hint::

    You can find this example in the :file:`examples/blog` folder in the
    GitHub repository.

Let's get started. We want to build a small blog with *sqlalchemy* and *flask*.


Models
------

First of all, we define our models in the :file:`models.py` file.

.. literalinclude:: /../../examples/blog/models.py
    :linenos:


View
----

.. todo::

    Write a browseable frontend.


Then we create the Flask appliaction and install the *py-jsonapi* extension
on it:

.. literalinclude:: /../../examples/blog/view.py
    :linenos:


Play with it
------------

.. note:: Content-Type

    The jsonapi specification requires that all requests must have the
    content-type `application/vnd.api+json`. So make sure to set this header
    correct, otherwise you will get a *UnknownMediaType* exception.

Use the http library of your choice and perform some requests against the
API. Here are some examples using *requests*:

.. literalinclude:: /../../examples/blog/client.py
    :linenos:
