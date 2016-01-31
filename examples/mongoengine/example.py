#!/usr/bin/env python3

import mongoengine

import jsonapi
import jsonapi.mongoengine


class User(mongoengine.Document):

    name = mongoengine.StringField()

    @jsonapi.marker.property.Attribute()
    def first_name(self):
        """
        The mongoengine serializer is a subclass of the markup based
        serializer. So you can also use the decorators from there in your
        models.
        """
        return self.name.split()[0]


class Post(mongoengine.Document):

    text = mongoengine.StringField()
    author = mongoengine.ReferenceField(User)


# Create the serializers for the models.
user_serializer = jsonapi.mongoengine.Serializer(User)
post_serializer = jsonapi.mongoengine.Serializer(Post)


# Create the mongoengine database adapter.
mongo_db = jsonapi.mongoengine.Database()


# Create the API
api = jsonapi.base.api.API("/api")
api.add_model(user_serializer, mongo_db)
api.add_model(post_serializer, mongo_db)
