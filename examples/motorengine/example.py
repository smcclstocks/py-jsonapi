#!/usr/bin/env python3

import motorengine

import jsonapi
import jsonapi.motorengine
import jsonapi.tornado

class User(motorengine.Document):

    name = motorengine.StringField()
    email = motorengine.EmailField()
    posts = motorengine.ListField(motorengine.ReferenceField("__main__.Post"))

class Post(motorengine.Document):

    text = motorengine.StringField()
    author = motorengine.ReferenceField(User)

# Use the motorengine schema for the models.
user_schema = jsonapi.motorengine.Schema(User)
post_schema = jsonapi.motorengine.Schema(Post)

# Create the motorengine database adapter.
db = jsonapi.motorengine.Database()

# Create the API
api = jsonapi.tornado.TornadoAPI("/api", db)
api.add_type(user_schema)
api.add_type(post_schema)
