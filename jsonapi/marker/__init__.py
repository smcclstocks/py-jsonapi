#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2016 Benedikt Schmitt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
jsonapi.marker
==============

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
*to-many* relationship also requires an *adder*:

.. literalinclude:: ../../examples/marker/tutorial.py
    :lines: 78-101

Creating the schema
~~~~~~~~~~~~~~~~~~~

The *Post* model is now complete and we want to create the serializer based on
our markup:

.. literalinclude:: ../../examples/marker/tutorial.py
    :lines: 104

API
---

.. automodule:: jsonapi.marker.method
.. automodule:: jsonapi.marker.property

"""

from . import method
from . import property
