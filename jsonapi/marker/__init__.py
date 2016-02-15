#!/usr/bin/env python3

"""
jsonapi.marker
==============

:license: GNU Affero General Public License v3

This package contains decorators for *attribute* and *relationship* methods
or properties. They can be used to create a *schema* on the fly.

The base :class:`~jsonapi.base.schema.Schema` find the decorated methods
automatic.

Tutorial
--------

.. hint::

    We will use the *property* decorators, which turn the decorated
    methods into properties. If you don't want to turn the methods into
    properties, you can use the decorators in :mod:`jsonapi.marker.method`
    instead of :mod:`jsonapi.marker.property`.

.. hint::

    This tutorial is also available in the examples folder:
    :file:`examples/marker/tutorial.py`

We will demonstrate the *decorators* on the following example with a *Post*
model.

.. literalinclude:: ../../examples/marker/tutorial.py
    :lines: 11-18

id attribute
~~~~~~~~~~~~

The *id_attribute* decorator must be used at least **once**, to tell the
serializer how it can find the id of an instance:

.. literalinclude:: ../../examples/marker/tutorial.py
    :lines: 21-26

attributes
~~~~~~~~~~

To mark an attribute, you can use the *Attribute* decorator. If you define no
setter, the attribute is *read-only* and can not be changed by clients.

The *attribute* marker accept some arguments. E.g.: If you want the attribute
to be displayed with a different name in the API, use the *name* argument.

.. literalinclude:: ../../examples/marker/tutorial.py
    :lines: 29-56

*to-one* relationships
~~~~~~~~~~~~~~~~~~~~~~

For *to-one* relationships, which can either be *None* or a *resource*,
you must use the *to_one_relationship* decorator.

.. literalinclude:: ../../examples/marker/tutorial.py
    :lines: 59-75

*to-many* relationships
~~~~~~~~~~~~~~~~~~~~~~~

If you want to mark a *to-many* relationship, which returns a *list* of
related resources, you must use the *to_many_relationship* decorator. However, a
*to-many* relationship also requires an *adder* and *remover*:

.. literalinclude:: ../../examples/marker/tutorial.py
    :lines: 78-115

Creating the schema
~~~~~~~~~~~~~~~~~~~

The *Post* model is now complete and we want to create the serializer based on
our markup:

.. literalinclude:: ../../examples/marker/tutorial.py
    :lines: 118

API
---

.. automodule:: jsonapi.marker.method
.. automodule:: jsonapi.marker.property

"""

from . import method
from . import property
