How to
======

You can use the decorators defined
:mod:`jsonapi.marker.method` and :mod:`jsonapi.marker.property` to mark
special methods and properties as attributes or relationship fields.

In the following example, we will define a *User* and *Post* model. Please note,
that the database link is not handled by the marker module. You still have to
use a database adapter.

.. literalinclude:: /../../examples/marker/models.py
    :linenos:
