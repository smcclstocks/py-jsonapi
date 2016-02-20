Todo
====

*   Implement the *bulk* extension

*   Implement OAuth2 support

*   Implement authorization (user session, OAuth2, ...)

*   Support client generated ids.

    http://jsonapi.org/format/#crud-creating-client-ids

*   Add *profile* support

    http://jsonapi.org/extensions/#profiles

*   Add a custom extension for *file* objects. A file marker could return a file
    like object or a local path.

*   Add support for the other status codes in POST or PATCH requests:

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

*   Throw an exception if an attribute or relationship should be changed, but
    is read only.
