#!/usr/bin/env python3

import mongoengine

import jsonapi
import jsonapi.mongoengine

class User(mongoengine.Document):

    name = mongoengine.StringField()
    email = mongoengine.EmailField()

class Post(mongoengine.Document):

    text = mongoengine.StringField()
    author = mongoengine.ReferenceField(User)

# Use the mongoengine schema for the models.
user_schema = jsonapi.mongoengine.Schema(User)
post_schema = jsonapi.mongoengine.Schema(Post)

# Create the mongoengine database adapter.
mongo_db = jsonapi.mongoengine.Database()

# Create the API
api = jsonapi.base.api.API("/api")
api.add_type(user_schema, mongo_db)
api.add_type(post_schema, mongo_db)
