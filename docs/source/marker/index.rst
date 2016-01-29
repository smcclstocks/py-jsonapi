Marker
======

.. toctree::
    :maxdepth: 1

    how_to

    markup
    method
    property
    serializer


This package creates a serializer by using something similar to an ORM:
The :class:`~jsonapi.marker.markup.Markup`. It essentially contains the fields
(attributes and relationship) methods, which are necessary to render a full
*JSONapi* response. Different **decorators** can be used to **mark**
attribute and relationship methods as well as the constructor, without having
to subclass the base serializer. Please take a look at the next page :)
