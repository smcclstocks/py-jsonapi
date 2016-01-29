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
jsonapi.marker.serializer
=========================
"""

# std
from collections import OrderedDict

# local
from .. import base


class Serializer(base.Serializer):
    """
    Serializes a resource based on the *markup*.

    :arg jsonapi.marker.markup.Markup markup:
    :arg jsonapi.base.api.API api:
    """

    def __init__(self, markup, api=None):
        """
        """
        self.markup = markup
        self.model = markup.model
        self.typename = markup.typename
        self.api = api
        return None

    # ID
    # ~~

    def id(self, resource):
        """
        """
        return str(self.markup.id_attribute.get(resource))

    # Creation
    # ~~~~~~~~

    def create_resource(self, attributes, relationships, meta):
        """
        """
        fields = dict()
        fields.update(attributes)
        fields.update(relationships)
        new_resource = self.markup.constructor.create(**fields)
        return new_resource

    # Attributes
    # ~~~~~~~~~~

    def attributes(self):
        """
        """
        return list(self.markup.attributes.keys())

    def get_attribute(self, resource, attr_name):
        """
        """
        attr = self.markup.attributes[attr_name]
        return attr.get(resource)

    def set_attribute(self, resource, attr_name, attr_value):
        """
        """
        attr = self.markup.attributes[attr_name]
        attr.set(resource, attr_value)
        return None

    # Relationships
    # ~~~~~~~~~~~~~

    def relationships(self):
        """
        """
        return self.markup.relationships.keys()

    def is_to_one_relationship(self, rel_name):
        """
        """
        rel = self.markup.relationships[rel_name]
        return rel.to_one

    def get_relative_id(self, resource, rel_name):
        """
        """
        rel = self.markup.relationships[rel_name]
        assert rel.to_one

        relative = rel.get(resource)
        if relative is not None:
            relative = base.utilities.ensure_identifier(self.api, relative)
        return relative

    def get_relative_ids(self, resource, rel_name):
        """
        """
        rel = self.markup.relationships[rel_name]
        assert rel.to_many

        relatives = rel.get(resource)
        relatives = [
            base.utilities.ensure_identifier(self.api, relative)\
            for relative in relatives\
            if relative is not None
        ]
        return relatives

    def set_relative(self, resource, rel_name, relative):
        """
        """
        rel = self.markup.relationships[rel_name]
        assert rel.to_one

        rel.set(resource, relative)
        return None

    def set_relatives(self, resource, rel_name, relatives):
        """
        """
        rel = self.markup.relationships[rel_name]
        assert rel.to_many

        rel.set(resource, relatives)
        return None

    def extend_relationship(self, resource, rel_name, relatives):
        """
        """
        rel = self.markup.relationships[rel_name]
        assert rel.to_many

        rel.extend(resource, relatives)
        return None
