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


    @jsonapi.marker.property.IDAttribute()
    def id(self):
        """
        The id attribute must be marked with the *IDAttribute* decorator.
        """
        return self._id


    @jsonapi.marker.property.Attribute(name="headline")
    def title(self):
        """
        Normal attributes can be marked with the *Attribute* decorator.

        Because the title is completly derived from the *text* attribute, we
        define no setter. If a client tries to change the value of *title*,
        a Forbidden http error will be thrown.
        """
        # Use the first line of the articles text as title, if not title
        # exists.
        title = self._text[:min(32, self._text.find("\n"))]
        return title


    @jsonapi.marker.property.Attribute()
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


    @jsonapi.marker.property.ToOneRelationship()
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


    @jsonapi.marker.property.ToManyRelationship()
    def comments(self):
        """
        Defining a *to-many* relationship requires a bit more effort. If it
        is writeable, you will have to define an *adder* and a *remover* in
        addition to the *setter*.
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
        markup must know how to add a new resource to the relationship and
        not only how to replace.
        """
        assert isinstance(comment, Comment)
        self._comments.append(comment)
        return None

    @comments.remover
    def remove_comment(self, comment):
        """
        We also must define a *remover*. If the comment is in the relationship,
        it will be removed. Otherwise nothing happens.
        """
        assert isinstance(comment, Comment)
        try:
            self._comments.remove(comment)
        except ValueError:
            pass
        return None


post_markup = jsonapi.marker.Markup(Post)
post_serializer = jsonapi.marker.Serializer(post_markup)

if __name__ == "__main__":
    print(post_serializer.attributes())
    print(post_serializer.relationships())
