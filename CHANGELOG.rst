Changelog
=========

*   0.3.0b0

    *   Removed the *remove()* method from the *to-many* relationship
        descriptor, because it is not needed.

*   0.2.1b0 - 0.2.6b0

    *   Added asyncio support
    *   Added motorengine

*   0.2.0b0

    *   The bulk database is now an extension
    *   The API now takes only one database adapter for all models. This removes
        one layer in the database hierarchy.
    *   The relationship schema's *delete* method has been renamed to *clear*
    *   The serializer has been split up into *Serializer* and *Unserializer*
    *   A dictionary ``_jsonapi``, which contains the serializer, typename,
        schema, ... is added to each resource class
    *   Everything that was names *model* is now named *resource_class*
