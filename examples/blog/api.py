#!/usr/bin/env python3

# third party
import jsonapi
import jsonapi.sqlalchemy
import jsonapi.flask

# local
import models
import db


__all__ = [
    "api"
]


# Create the API.
api = jsonapi.flask.FlaskAPI("/api")

# Create the database adapter.
sql_db = jsonapi.sqlalchemy.Database(sessionmaker=db.Session)

# Create the serializers.
user_serializer = jsonapi.sqlalchemy.Serializer(models.User)
post_serializer = jsonapi.sqlalchemy.Serializer(models.Post)
comment_serializer = jsonapi.sqlalchemy.Serializer(models.Comment)

# Add the resource classes.
api.add_model(user_serializer, sql_db)
api.add_model(post_serializer, sql_db)
api.add_model(comment_serializer, sql_db)
