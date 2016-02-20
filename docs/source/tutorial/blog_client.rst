Blog API Client
===============

.. hint::

    We support the full basic JSONapi specification. So this example is only
    a short demonstration of *py-jsonapi*. Please read the full specification
    at http://jsonapi.org/format/ for more information.

We use the `requests <http://docs.python-requests.org/en/master/>`_ library for
the *http* requests. You can install it with *pip*.

Creating Resources
------------------

.. seealso::

    http://jsonapi.org/format/#crud-creating

First of all, we create some users:

.. code-block:: python3

    def create_user(name):
        r = requests.post(
            "http://localhost:5000/api/User",
            headers={
                "content-type": "application/vnd.api+json"
            },
            data=json.dumps({
                "data": {
                    "type": "User",
                    "attributes": {
                        "name": name
                    }
                }
            })
        )
        return r.json()

    homer = create_user("Homer Simpson").get("data")
    marge = create_user("Marge Simpson").get("data")
    bart = create_user("Bart Simpson").get("data")
    lisa = create_user("Lisa Simpson").get("data")
    maggie = create_user("Maggie Simpson").get("data")
    mr_burns = create_user("Charles Montgomery Burns").get("data")
    murphy = create_user("Bleeding Gums Murphy").get("data")

Next, we write some posts:

.. code-block:: python3

    def create_post(text, author_id):
        r = requests.post(
            "http://localhost:5000/api/Post",
            headers={
                "content-type": "application/vnd.api+json"
            },
            data=json.dumps({
                "data": {
                    "type": "Post",
                    "attributes": {
                        "text": text,
                    },
                    "relationships" :{
                        "author": {
                            "data": {
                                "type": "User",
                                "id": author_id
                            }
                        }
                    }
                }
            })
        )
        return r.json()

    nuclear_plant_post = create_post(
        text="Studie hat gezeigt: Atomkraftwerke beugen Rueckenschmerzen vor.",
        author_id=mr_burns["id"]
    ).get("data")
    monorail_post = create_post(
        text="Monorail is faster than the Flash.",
        author_id=maggie["id"]
    ).get("data")

Because it's not 1999, we allow users to comment our posts and if they want,
they can start a shit storm in the comment section:

.. code-block:: python3

    def create_comment(text, author_id, post_id):
        r = requests.post(
            "http://localhost:5000/api/Comment",
            headers={
                "content-type": "application/vnd.api+json"
            },
            data=json.dumps({
                "data": {
                    "type": "Comment",
                    "attributes": {
                        "text": text
                    },
                    "relationships": {
                        "author": {
                            "data": {"type": "User", "id": author_id}
                        },
                        "post": {
                            "data": {"type": "Post", "id": post_id}
                        }
                    }
                }
            })
        )
        return r.json()

    nuclear_plant_comment = create_comment(
        text="You're a wizard Harry!",
        author_id=lisa["id"],
        post_id=nuclear_plant_post["id"]
    ).get("data")

Querying Collections
--------------------

.. seealso::

    http://jsonapi.org/format/#fetching

If you want to get all resources of a specific type, you only have to perform
a *GET* request to the collection endpoint:

.. code-block:: python3

    def get_users():
        r = requests.get(
            "http://localhost:5000/api/User/",
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

Filter
~~~~~~

.. hint::

    The filter keyword is only reserved by the JSONapi specification, but not
    described. The filter syntax and semantics used here, may differ from
    other implementations.

.. seealso::

    http://jsonapi.org/format/#fetching-filtering

You can filter the results by applying one or multiple filters. The filters
are always combined with a logical ``and``. Which filters are supported and
which not, depends on the used database driver and schema. You can take a look
at :attr:`~jsonapi.base.request.Request.japi_filters` for a list of all filter
names.

In the following example, we want to know all users with ``simpson`` in their
name. To get them, we use the case insensitive `icontains` filter:

.. code-block:: python3

    def filter_users():
        r = requests.get(
            "http://localhost:5000/api/User/",
            params={
                # case insensitive *contains*
                "filter[name]": "icontains:\"simpson\""
            },
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

Limit
~~~~~

.. hint::

    This query parameter is not defined by the official JSONapi specification.

You can limit the number of returned resources with the *limit* query parameter:

.. code-block:: python3

    def limit_users():
        r = requests.get(
            "http://localhost:5000/api/User/",
            params={
                "limit": 2,
                "sort": "name"
            },
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

Offset
~~~~~~

.. hint::

    This query parameter is not defined by the official JSONapi specification.

A *limit* without *offset* is quite useless, so we also support the *offset*
query parameter:

.. code-block:: python3

    def offset_users():
        r = requests.get(
            "http://localhost:5000/api/User/",
            params={
                "offset": 2,
                "limit": 2,
                "sort": "name"
            },
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

Pagination
~~~~~~~~~~

.. seealso::

    http://jsonapi.org/format/#fetching-pagination

We use a page based strategy for the pagination. You can supply the
``page[number]`` and ``page[size]`` query parameters. The first page has the
number **1**.

Please note, that you must supply ``page[size]`` and ``page[number]`` for the
pagination. If only one parameter is present, the pagination does not work.

The *limit* and *offset* parameters are ignored, if the pagination is used.

.. code-block:: python3

    def paginate_users():
        r = requests.get(
            "http://localhost:5000/api/User/",
            params={
                "page[number]": 2,
                "page[size]": 5,
                "sort": "name"
            },
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

You can find links to the *next*, *previous*, *first*, *last* and *current*
page in the *meta* object of the response.

Sparse Fieldsets
~~~~~~~~~~~~~~~~

.. seealso::

    http://jsonapi.org/format/#fetching-sparse-fieldsets

You can request specific fields of a resource type by using the
``fields[typename]`` query parameter. All other fields will not be included
into the response.

In the next example, we query all users and include their posts. However, we
don't want to know the comments written by the users, so we request only the
*name* and *posts* fields. For posts, we are only interested in the *text*
field.

.. code-block:: python3

    def sparse_fieldset_users():
        r = requests.get(
            "http://localhost:5000/api/User/",
            params={
                "fields[User]": "name,posts",
                "fields[Post]": "text",
                "include": "posts"
            },
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

Sorting
~~~~~~~

.. seealso::

    http://jsonapi.org/format/#fetching-sorting

You can sort the resources by applying one or multiple sort criteria.
To sort the users by their names in ascending order, use ``"+name"`` or
simply ``"name"`` as criterion and ``"-name"`` for descending order.

If you supply multiple criteria, the resources are grouped by the first
criterion, then by the second and so on.

Please note, that if a field can be used for sorting or not, is determined by
the database adapter and the used schema. For example: The *sqlalchemy*
adapter currently supports sorting only for *attributes*.

.. code-block:: python3

    def sort_users_asc():
        r = requests.get(
            "http://localhost:5000/api/User/",
            params={
                # alternative:
                #
                #   "sort": "+name"
                "sort": "name"
            },
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

    def sort_users_desc():
        r = requests.get(
            "http://localhost:5000/api/User/",
            params={
                "sort": "-name"
            },
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

Inclusion of Related Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    http://jsonapi.org/format/#fetching-includes

You can include related resources by supplying the ``include`` parameter.

In the next example, we want to include the *posts* written by the users and the
*comments* of these posts into the response.

.. code-block:: python3

    def include_user_posts():
        r = requests.get(
            "http://localhost:5000/api/User/",
            params={
                "include": "posts,posts.comments"
            },
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

Fetching and Updating Resources
-------------------------------

.. seealso::

    http://jsonapi.org/format/#fetching-resources

You can query a specific resource by its type and id:

.. code-block:: python3

    def get_user(user_id):
        r = requests.get(
            "http://localhost:5000/api/User/{}".format(user_id),
            headers={
                "content-type": "application/vnd.api+json"
            },
        )
        return r.json()

Updating Resources
~~~~~~~~~~~~~~~~~~

.. seealso::

    http://jsonapi.org/format/#crud-updating

Resources are updated by performing a *PATCH* request to the resource's uri:

.. code-block:: python3

    def update_user(user_id, name):
        r = requests.patch(
            "http://localhost:5000/api/User/{}".format(user_id),
            headers={
                "content-type": "application/vnd.api+json"
            },
            data=json.dumps({
                "data": {
                    "type": "User",
                    "id": user_id,
                    "attributes": {
                        "name": name
                    }
                }
            })
        )
        return r.json()

    homer = update_user(homer["id"], "HoMeR SiMpSoN")

Deleting Resources
~~~~~~~~~~~~~~~~~~

.. seealso::

    http://jsonapi.org/format/#crud-deleting

You can delete a resource by performing a *DELETE* request to the resource's
uri:

.. code-block:: python3

    def delete_user(user_id):
        r = requests.delete(
            "http://localhost:5000/api/User/{}".format(user_id),
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.status_code

    delete_user(murphy["id"])

Relationships Endpoint
----------------------

.. seealso::

    http://jsonapi.org/format/#fetching-relationships

You can fetch and manipulate relationships using the *relationships endpoint*.

Updating Relationships
----------------------

To change the author of a post, you must sent a *PATCH* request to the
relationship endpoint:

.. code-block:: python3

    def update_post_author(post_id, author_id):
        r = requests.patch(
            "http://localhost:5000/api/Post/{}/relationships/author".format(post_id),
            headers={
                "content-type": "application/vnd.api+json"
            },
            data=json.dumps({
                "data": {
                    "id": author_id,
                    "type": "User"
                }
            })
        )
        return r.json()

    update_post_author(monorail_post["id"], homer["id"])

Deleting Relationships
~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    http://jsonapi.org/format/#crud-updating-relationships

You can set a *to-one* relationship to *null* or clear a *to-many* relationship
by performing a *DELETE* request to the relationships endpoint:

.. code-block:: python3

    def delete_post_comments(post_id):
        r = requests.delete(
            "http://localhost:5000/api/Post/{}/relationships/comments".format(post_id),
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

Extending Relationships
~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    http://jsonapi.org/format/#crud-updating-relationships

You can add new resources to a *to-many* relationship with the *POST* http
method:

.. code-block:: python3

    def add_post_comment(post_id, comment_id):
        r = requests.post(
            "http://localhost:5000/api/Post/{}/relationships/comments".format(post_id),
            headers={
                "content-type": "application/vnd.api+json"
            },
            data=json.dumps({
                "data": [{"type": "Comment", "id": str(comment_id)}]
            })
        )
        return r.json()

Related Resources
-----------------

.. seealso::

    http://jsonapi.org/format/#fetching

Related resources can be easily fetched with a *GET* request to the
*related* endpoint:

.. code-block:: python3

    def get_post_comments(post_id):
        r = requests.get(
            "http://localhost:5000/api/Post/{}/comments".format(post_id),
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()

    def get_post_author(post_id):
        r = requests.get(
            "http://localhost:5000/api/Post/{}/author".format(post_id),
            headers={
                "content-type": "application/vnd.api+json"
            }
        )
        return r.json()
