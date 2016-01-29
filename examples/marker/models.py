#!/usr/bin/env python3

# third party
import jsonapi
import jsonapi.marker


class User(object):
    """
    For this model, we use the *method* markers. These decorators leave a
    method as method and do **not** turn them into properties. So you can
    call the methods as usual:

    .. code-block:: python3

        >>> homer = User(id="42", "Homer Simpson")
        >>> homer.id()
        "42"
        >>> homer.name()
        "Homer Simpson"
        >>> homer.set_name("Max Power")
        >>> homer.name()
        "Max Power"
        >>> homer.posts()
        []
    """

    def __init__(self, id="", name="", posts=None):
        self._id = id
        self._name = name
        self._posts = posts or list()
        return None

    @jsonapi.marker.method.IDAttribute()
    def id(self):
        """
        If you want, you can define a setter with
        """
        return self._id

    @jsonapi.marker.method.Attribute()
    def name(self):
        return self._name

    @name.setter
    def set_name(self, name):
        self._name = name

    @jsonapi.marker.method.ToManyRelationship()
    def posts(self):
        return self._posts

    @posts.setter
    def set_posts(self, posts):
        self._posts = posts
        return None

    @posts.adder
    def add_post(self, post):
        self._post.append(post)
        return None

    @posts.remover
    def remove_post(self, post):
        self._post.remove(post)
        return None


class Post(object):
    """
    For this model, we the *property* markers, which turn the methods into
    Python properties. Please note, that you are free to use method and property
    markers in the same model.

    .. code-block:: python3

        >>> post = Post(
        ...     id="101010", text="Monorail built in Springfield!",
        ...     author=homer
        ... )
        >>> post.id
        "101010"
        >>> post.text
        "Monorail built in Springfield!"
        >>> post.text = "Monorail destroyed!"
        >>> post.text
        "Monorail destroyed!"
        >>> post.author
        <User objects at 0x....>
        >>> post.author = None
    """

    def __init__(self, id=None, text=None, author=None):
        self._id = id
        self._text = text
        self._author = author
        return None

    @jsonapi.marker.property.IDAttribute()
    def id(self):
        return self._id

    @jsonapi.marker.property.Attribute()
    def text(self):
        return self._text

    @text.setter
    def text(self):
        return self._text

    @jsonapi.marker.property.ToOneRelationship()
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author


# Create the markups
user_markup = jsonapi.marker.Markup(User)
post_markup = jsonapi.marker.Markup(Post)

# Create the serializers based upon the markups.
user_serializer = jsonapi.marker.Serializer(user_markup)
post_serializer = jsonapi.marker.Serializer(post_markup)

# Print some information
print(user_serializer.attributes())
print(user_serializer.relationships())
print()

print(post_serializer.attributes())
print(post_serializer.relationships())
print()

# Create a new resource using the marup.
homer = user_markup.constructor.create(name="Homer Simpson", id="42")
print(user_markup.id_attribute.get(homer))
print(user_markup.attributes["name"].get(homer))
print(user_markup.relationships["posts"].get(homer))
