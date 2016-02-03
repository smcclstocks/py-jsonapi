#!/usr/bin/env python3

"""
jsonapi.base.handler
====================

:license: GNU Affero General Public License v3
:copyright: 2016 by Benedikt Schmitt <benedikt@benediktschmitt.de>

.. automodule:: jsonapi.base.handler.base
.. automodule:: jsonapi.base.handler.collection
.. automodule:: jsonapi.base.handler.related
.. automodule:: jsonapi.base.handler.relationship
.. automodule:: jsonapi.base.handler.resource
"""

# local
from .base import BaseHandler
from .collection import CollectionHandler
from .related import RelatedHandler
from .relationship import RelationshipHandler
from .resource import ResourceHandler
