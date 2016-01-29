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

# local
from .. import marker
from .marker import SQLAlchemyMarkup


__all__ = [
    "Serializer"
]


class Serializer(marker.Serializer):
    """
    The same as as :class:`jsonapi.marker.serializer.Serializer`, but
    uses the :class:`~jsonapi.sqlalchemy.marker.SQLAlchemyMarkup` for the model
    per default.
    """

    def __init__(self, model, api=None):
        """
        """
        markup_ = SQLAlchemyMarkup(model)
        super().__init__(markup_, api)
        return None
