#!/usr/bin/env python3

# py-jsonapi - A toolkit for building a JSONapi
# Copyright (C) 2016 Benedikt Schmitt <benedikt@benediktschmitt.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
jsonapi.marker.method
=====================

This module contains decorators for **methods**.
"""

# local
from . import markup


__all__ = [
    "Attribute",
    "IDAttribute",
    "ToOneRelationship",
    "ToManyRelationship",
    "Constructor"
]


class BaseMarker(object):
    """
    This is the base class for the attribute and relationship markers. It
    basically has the same properties as the built-in Python `property()`
    decorator, but does not turn functions into properties.
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

            # This will the constructor first and the `@` will call the object
            # created with the constructor.
        """
        return self.getter(*args, **kargs)

    def __get__(self, resource, type_=None):
        """
        """
        if not resource:
            return self

        def tmp(*args, **kargs):
            return self.get(resource, *args, **kargs)
        return tmp

    def getter(self, f):
        """
        Descriptor to change the :attr:`fget` function.
        """
        if self.name is None:
            self.name = f.__name__
        if self.__doc__ is None:
            self.__doc__ = f.__doc__
        self.fget = f

        # Note, that we return self.
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

class Attribute(BaseMarker, markup.Attribute):
    """
    Can be used to mark JSONapi attributes on a class:

    .. code-block:: python3

        class User(object):

            # Way 1: As decorator

            @Attribute()
            def email(self):
                return self._email

            @email.setter
            def set_email(self, new_addr):
                self._email = new_addr

            # Way 2: As new attribute

            def last_edited(self):
                return self._last_edited

            jlast_edited = Attribute(fget=last_edited)

    :seealso: :class:`IDAttribute`
    """


class IDAttribute(BaseMarker, markup.IDAttribute):
    """
    Works like :class:`Attribute`, but must be used for the id attribute.
    """


# Relationships
# ~~~~~~~~~~~~~

class ToOneRelationship(BaseMarker, markup.ToOneRelationship):
    """
    This marker can be used to mark a *to-one* relationship on a class:

    .. code-block:: python3

        class Post(object):

            @ToOneRelationship()
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

    :seealso: :class:`ToManyRelationship`
    """


class ToManyRelationship(BaseMarker, markup.ToManyRelationship):
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

            @comments.remover
            def remove_comment(self, comment):
                self._comments.remove(comment)
                return None

    :seealso: :class:`ToOneRelationship`

    :arg fget:
    :arg fset:
    :arg fdel:
    :arg fadd:
        A function used for adding a new object to the relationship.
    :arg fextend:
        A funtion used to add a list of objects to the relationship.
    :arg frem:
        A function used to remove an object from the relationship.
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

    def remover(self, f):
        """
        Descriptor to change the :attr:`frem` function.
        """
        self.frem = f
        return f

    def add(self, resource, relative):
        return self.fadd(resource, relative)

    def extend(self, resource, relatives):
        if self.fextend is not None:
            return self.fextend(resource, relatives)
        else:
            return super().extend(resource, relatives)

    def remove(self, resource, relative):
        return self.frem(resource, relative)


# Construction
# ~~~~~~~~~~~~

class Constructor(classmethod, markup.Constructor):
    """
    Can be used, to mark a constructor method. Please note, that a constructor
    function is always a **classmethod**.

    If you don't use a special constructor method, the default ``__init__``
    constructor is used automatic.

    .. code-block:: python3

        class User(object):

            @Constructor()
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
