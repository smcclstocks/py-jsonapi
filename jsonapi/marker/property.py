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
jsonapi.marker.property
=======================

This module contains decorators for **properties**.
"""

# local
from . import method


# Attribute
# ~~~~~~~~~

class Attribute(method.PropertyMixin, method.Attribute):
    """
    The same as :class:`jsonapi.marker.method.Attribute`,
    but emulates a Python `property()`.
    """


class IDAttribute(method.PropertyMixin, method.IDAttribute):
    """
    The same as :class:`jsonapi.marker.method.IDAttribute`,
    but emulates a Python `property()`.
    """


# Relationships
# ~~~~~~~~~~~~~

class ToOneRelationship(method.PropertyMixin, method.ToOneRelationship):
    """
    The same as :class:`jsonapi.marker.method.ToOneRelationship`,
    but emulates a Python `property()`.
    """


class ToManyRelationship(method.PropertyMixin, method.ToManyRelationship):
    """
    The same as :class:`jsonapi.marker.method.ToOneRelationship`,
    but emulates a Python `property()`.
    """
