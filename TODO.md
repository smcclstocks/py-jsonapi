# TODO


*   If attributes or fields or whatever are not writeable (readonly), throw
    a Forbidden http exception. To achieve this, the serializer must be
    extended.

*   Add marker for *links* documents
    These marker must support resource link documents and relationship
    documents.

    http://jsonapi.org/format/#document-links

*   Add marker for *meta* document
    These markers must support resource meta, relationship meta and link meta
    documents.

    http://jsonapi.org/format/#document-meta

*   Implement support for OAuth2 authorization

*   Implement support for user based queries (*where user_id=current_user*)

*   Support client generated ids.

    http://jsonapi.org/format/#crud-creating-client-ids

*   Make use of other status codes in POST or PATCH requests:

    *   202 Accepted

        If the request has been accepted, but processing did not finish.
        This can be done by adding an attribute *async=bool()* to the setter
        methods.

    *   203 No Content

        If the update was successful and no other attributes changed

        Solution:
        Add an attribute *has_sideeffects=bool()* or *affects=[]*, which
        indicates if a *setter* also changes other fields and which.

    *   409 Conflict

        If the update violates a constraint

        Solution: Create a *Conflict* exception

*   Implement the *bulk* extension

*   Add support for asyncio.

*   Add *profile* support

    http://jsonapi.org/extensions/#profiles

*   Add a custom extension for *file* objects. A file marker could return a file
    like object or a local path.
