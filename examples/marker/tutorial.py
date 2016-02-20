#!/usr/bin/env python3

# NOTE:
#
#   If you change this file, make sure, that the documentation
#   still builds correct, since we use literalinclude with the lines option
#   there.

import jsonapi

class Post(object):

    def __init__(self, id="", text="", author=None, comments=None):
        self._id = id
        self._text = text
        self._author = author
        self._comments = comments or list()
        return None


    @jsonapi.marker.property.id_attribute()
    def id(self):
        """
        The id attribute must be marked with the *id_attribute* decorator.
        """
        return self._id


    @jsonapi.marker.property.attribute(name="headline")
    def title(self):
        """
        Normal attributes can be marked with the *attribute* decorator.

        Because the title is completly derived from the *text* attribute, we
        define no setter. If a client tries to change the value of *title*,
        a Forbidden http error will be thrown.
        """
        # Use the first line of the articles text as title, if not title
        # exists.
        title = self._text[:min(32, self._text.find("\n"))]
        return title


    @jsonapi.marker.property.attribute()
    def text(self):
        """
        In contrary to the *title* attribute, the *text* can be changed.
        To achieve this, we can define a *setter*, just like for every other
        Python property.
        """
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        return None


    @jsonapi.marker.property.to_one_relationship()
    def author(self):
        """
        This property describes a *to-one* relationship. The *author* is turned
        into a Python property.

        Because *py-jsonapi* allows polymorphism, we don't force you to define
        the target type of the returned object. The API will determine the
        type of the related resource automatic.
        """
        return self._author

    @author.setter
    def author(self, author):
        assert isinstance(author, User) or author is None
        self._author = author
        return None


    @jsonapi.marker.property.to_many_relationship()
    def comments(self):
        """
        Defining a *to-many* relationship requires a bit more effort. You must
        define an *adder* in addition to the *setter*.
        """
        return self._comments

    @comments.setter
    def comments(self, comments):
        assert all(isinstance(comment, Comment) for comment in comments)
        self._comments = comments
        return None

    @comments.adder
    def add_comment(self, comment):
        """
        Because we can add new resources to a *to-many* relationship, the
        schema must know how to add a new resource to the relationship and
        not only how to replace.
        """
        assert isinstance(comment, Comment)
        self._comments.append(comment)
        return None


post_schema = jsonapi.base.schema.Schema(Post)

if __name__ == "__main__":
    print(post_schema.attributes)
    print(post_schema.relationships)
