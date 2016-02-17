#!/usr/bin/env python3

"""
jsonapi.asyncio.serializer
==========================

:license: GNU Affero General Public License v3

Contains an *unserializer* that works with asynchronous database drivers.
"""

# std
import logging

# local
import jsonapi
from jsonapi.base import errors


__all__ = [
    "Unserializer"
]


LOG = logging.getLogger(__file__)


class Unserializer(jsonapi.base.serializer.Unserializer):
    """
    Does the same as the *base* Unserializer, but calls the database methods
    with *await*.
    """

    async def _load_relationships_object(self, db, relationships_object):
        """
        The same as the base class method, but calls the *db* async.
        """
        # Collect the identifiers.
        identifiers = set()
        for relname, relobj in relationships_object.items():
            reldata = relobj.get("data")

            # *to-one* relationship (with target)
            # -> a single resource identifier object
            if isinstance(reldata, dict):
                identifiers.add((reldata["type"], reldata["id"]))

            # *to-many* relationship
            # -> a list of resource identifier objects
            elif isinstance(reldata, list):
                identifiers.update(
                    (item["type"], item["id"]) for item in reldata
                )

        # Load the resources
        relatives = await db.get_many(identifiers, required=True)

        # Map the relationship names back to the related resources.
        result = dict()
        for relname, relobj in relationships_object.items():
            if "data" in relobj:
                reldata = relobj["data"]

                # *to-one* relationship with no target
                if reldata is None:
                    result[relname] = None
                # *to-one* relationship with target
                elif isinstance(reldata, dict):
                    identifier = (reldata["type"], reldata["id"])
                    result[relname] = relatives[identifier]
                # *to-many* relationship
                elif isinstance(reldata, list):
                    identifiers = [
                        (item["type"], item["id"]) for item in reldata
                    ]
                    result[relname] = [
                        relatives[identifier] for identifier in identifiers
                    ]
        return result

    async def create_resource(self, db, resource_object):
        """
        The same as the base class method, but calls *db* async.
        """
        assert resource_object["type"] == self.schema.typename

        # Load all relatives
        relationships = resource_object.get("relationships", dict())
        relationships = await self._load_relationships_object(db, relationships)

        # Get the attributes
        attributes = resource_object.get("attributes", dict())

        # Create the new resource.
        fields = dict()
        fields.update(attributes)
        fields.update(relationships)
        resource = self.schema.constructor.create(**fields)
        return resource

    async def update_resource(self, db, resource, resource_object):
        """
        The same as the base class method, but call the *db* async.
        """
        assert resource_object["id"] == self.schema.id_attribute.get(resource)
        assert resource_object["type"] == self.schema.typename

        # Save all errors, which occur during the update.
        error_list = errors.ErrorList()

        # Update the attributes
        if "attributes" in resource_object:
            try:
                self.update_attributes(resource, resource_object["attributes"])
            except errors.Error as err:
                error_list.append(err)
            except errors.ErrorList as err:
                error_list.extend(err)

        # Update the relationships
        if "relationships" in resource_object:
            rels_object = resource_object["relationships"]
            for rel_name, rel_object in rels_object.items():
                try:
                    await self.update_relationship(db, resource, rel_name, rel_object)
                except errors.Error as err:
                    error_list.append(err)
                except errors.ErrorList as err:
                    error_list.extend(err)

        if error_list:
            raise error_list
        return None

    async def update_relationship(
        self, db, resource, relationship_name, relationship_object
        ):
        """
        The same as the base class method, but calls the *db* async.
        """
        relationship = self.schema.relationships[relationship_name]

        # Break if no data key is given.
        if not "data" in relationship_object:
            return None

        # Update a *to-one* relationship
        if relationship.to_one:
            identifier = relationship_object["data"]
            if identifier is None:
                relative = None
            else:
                identifier = (identifier["type"], identifier["id"])
                relative = await db.get(identifier, required=True)
            relationship.set(resource, relative)

        # Update a *to-many* relationship
        else:
            identifiers = relationship_object["data"]
            identifiers = [(item["type"], item["id"]) for item in identifiers]

            relatives = await db.get_many(identifiers, required=True)
            relatives = list(relatives.values())

            relationship.set(resource, relatives)
        return None

    async def extend_relationship(
        self, db, resource, relationship_name, relationship_object
        ):
        """
        The same as the base class method, but calls the *db* async.
        """
        relationship = self.schema.relationships[relationship_name]
        assert relationship.to_many

        if "data" in relationship_object:
            # Get the identifier tuples of the new relatives.
            identifiers = relationship_object["data"]
            identifiers = [(item["type"], item["id"]) for item in identifiers]

            # Load the new relatives.
            relatives = await db.get_many(identifiers, required=True)
            relatives = list(relatives.values())

            relationship.extend(resource, relatives)
        return None
