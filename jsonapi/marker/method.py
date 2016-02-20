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
jsonapi.marker.method
=====================

This module contains the decorators for methods.

.. code-block:: python3

    class User(object):

        @attribute()
        def name(self):
            return self._name

        @name.setter
        def set_name(self, name):
            self._name = name.strip()
            return None

    # The decorated methods must still be called as methods:
    user = User()
    user.set_name("Homer")
    print(user.name())
"""

# local
import jsonapi


__all__ = [
    "attribute",
    "id_attribute",
    "to_one_relationship",
    "to_many_relationship",
    "constructor"
]


class BaseMarker(object):
    """
    This is the base class for the attribute and relationship markers. It
    basically has the same properties as the built-in Python `property()`
    decorator, but does **not** turn functions into properties.
    However, one can use the :class:`PropertyMixin`, to let it behave like
    a Python `property()`.

    :arg fget:
        A function used for getting the attribute value
    :arg fset:
        A function used for setting the attribute value
    :arg fdel:
        A function used for deleting the attribute.
    :arg str doc:
        The documentation of the attribute
    :arg str name:
        The name of the property shown in the API. In JSONapi terms, this
        is the *field* name.
    """

    def __init__(
            self, fget=None, fset=None, fdel=None, doc=None, name=None
        ):
        """
        """
        if doc is not None:
            self.__doc__ = doc
        elif fget is not None:
            self.__doc__ = fget.__doc__
        else:
            self.__doc__ = None

        if name is not None:
            self.name = name
        elif fget is not None:
            self.name = fget.__name__
        else:
            self.name = None

        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        return None

    def __call__(self, *args, **kargs):
        """
        Overriding `call` allows us to use the constructor:

        .. code-block::

            @BaseMarker(name="foobar")
            def foo(self):
                return self._foobar

            # This will call the constructor first and the `@` will call the
            # object created with the constructor.
        """
        return self.getter(*args, **kargs)

    def __get__(self, resource, type_=None):
        """
        """
        if not resource:
            return self
        return functools.partial(self.get, resource)

    def getter(self, f):
        """
        Descriptor to change the :attr:`fget` function.
        """
        if self.name is None:
            self.name = f.__name__
        if self.__doc__ is None:
            self.__doc__ = f.__doc__
        self.fget = f

        # Please note, that we return *self*.
        return self

    def setter(self, f):
        """
        Descriptor to change the :attr:`fset` function.
        """
        self.fset = f
        return f

    def deleter(self, f):
        """
        Descriptor to change the :attr:`fdel` function.
        """
        self.fdel = f
        return f

    def get(self, resource):
        return self.fget(resource)

    def set(self, resource, value):
        return self.fset(resource, value)

    def delete(self, resource):
        return self.fdel(resource)


class PropertyMixin(object):
    """
    Defines a mixin class, which can be used in combination with the
    :class:`BaseMarker`. It overrides the descriptor methods, so that a real
    Python propery is emulated.
    """

    def __get__(self, resource, type_=None):
        return self if resource is None else self.get(resource)

    def __set__(self, resource, value):
        return self.set(resource, value)

    def __delete__(self, resource):
        return self.delete(resource)

    def setter(self, f):
        self.fset = f
        # Returns self instead of f.
        return self

    def deleter(self, f):
        self.fdel = f
        # Returns self instead of f.
        return self


# Attribute
# ~~~~~~~~~

class attribute(BaseMarker, jsonapi.base.schema.Attribute):
    """
    Can be used to mark JSONapi attributes on a class:

    .. code-block:: python3

        class User(object):

            # Way 1: As decorator
            # This will replace the method with a transparent descriptor.

            @Attribute()
            def email(self):
                return self._email

            @email.setter
            def set_email(self, new_addr):
                self._email = new_addr

            # Way 2: As new attribute
            # This will not change the method at all.

            def last_edited(self):
                return self._last_edited

            jlast_edited = Attribute(fget=last_edited)

    :seealso: :class:`id_attribute`
    """


class id_attribute(BaseMarker, jsonapi.base.schema.IDAttribute):
    """
    Works like :class:`Attribute`, but must be used for the id attribute.
    """


# Relationships
# ~~~~~~~~~~~~~

class to_one_relationship(BaseMarker, jsonapi.base.schema.ToOneRelationship):
    """
    This marker can be used to mark a *to-one* relationship on a class:

    .. code-block:: python3

        class Post(object):

            @to_one_relationship()
            def author(self):
                '''
                This method may either return a JSONapi identifier, a two tuple
                `(typename, id)` with the id or the actual *author* object.
                '''
                return self._author

            @author.setter
            def set_author(self, new_author):
                '''
                *new_author* is either None or the new author object. **Not**
                just a simple identifier.
                '''
                self._new_author = new_author
                return None

    :seealso: :class:`to_many_relationship`
    """


class to_many_relationship(BaseMarker, jsonapi.base.schema.ToManyRelationship):
    """
    This marker can be used to mark a *to-many* relationship on a class:

    .. code-block:: python3

        class Post(object):

            @ToManyRelationship()
            def comments(self):
                return self._comments

            @comments.setter
            def set_comments(self, comments):
                '''
                *comments* is a list of comment objects.
                '''
                self._comments = comments
                return None

            @comments.adder
            def add_comment(self, comment):
                self._comments.append(comment)
                return None

    :seealso: :class:`ToOneRelationship`

    :arg fget:
    :arg fset:
    :arg fdel:
    :arg fadd:
        A function used for adding a new object to the relationship.
    :arg fextend:
        A funtion used to add a list of objects to the relationship.
    :arg doc:
    :arg name:
    """

    def __init__(
        self, fget=None, fset=None, fdel=None, fadd=None, fextend=None,
        frem=None, doc=None, name=None
        ):
        super().__init__(fget, fset, fdel, doc, name)

        self.fadd = fadd
        self.frem = frem
        return None

    def adder(self, f):
        """
        Descriptor to change the :attr:`fadd` function.
        """
        self.fadd = f
        return f

    def extender(self, f):
        """
        Descriptor to change the :attr:`fextend` function.
        """
        self.fextend = f
        return f

    def add(self, resource, relative):
        return self.fadd(resource, relative)

    def extend(self, resource, relatives):
        if self.fextend is not None:
            return self.fextend(resource, relatives)
        else:
            return super().extend(resource, relatives)


# Construction
# ~~~~~~~~~~~~

class constructor(classmethod, jsonapi.base.schema.Constructor):
    """
    Can be used, to mark a constructor method. Please note, that a constructor
    function is always a **classmethod**.

    If you don't use a special constructor method, the default ``__init__``
    constructor is used automatic.

    .. code-block:: python3

        class User(object):

            @constructor()
            def create(cls, name, email, posts):
                '''
                This method receives all attributes and related resources
                sent in the POST request, which is used to create a new
                resource.
                '''
                new_user = cls()
                new_user.set_email(email)
                new_user.set_posts(posts)
                return new_user
    """

    def create(self, **kargs):
        """
        Calls the decorated method and returns the result.
        """
        return self(**kargs)
