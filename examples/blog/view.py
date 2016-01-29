#!/usr/bin/env python3

# std
import uuid

# third party
import flask

import jsonapi
import jsonapi.flask
import jsonapi.sqlalchemy

import sqlalchemy
import sqlalchemy.orm

# local
import models


# Create the sqlalchemy database engine and a session maker.
engine = sqlalchemy.create_engine("sqlite:////tmp/" + uuid.uuid4().hex, echo=True)
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
models.Base.metadata.create_all(engine)


def create_api():
    """
    Create the API

    The collections will be available under:

        '/api/User', '/api/Post' and '/api/Comment'

    The SQLAlchemy adapter in py-jsonapi expects a function, which returns
    a valid session object. So we simply use our own sessionmaker.
    """
    api = jsonapi.flask.FlaskAPI(
        uri="/api",
        settings={
            "sqlalchemy_sessionmaker": Session
        }
    )

    # The database adapter tells us how to load and save resources. The
    # serializer tells us how to serialize a resource into a JSONapi
    # representation. In our cases, all of our models are sqlalchemy models.
    # So we use the SQLAlchemy database adapter and serializer.
    sql_db = jsonapi.sqlalchemy.Database()
    user_serializer = jsonapi.sqlalchemy.Serializer(models.User)
    post_serializer = jsonapi.sqlalchemy.Serializer(models.Post)
    comments_serializer = jsonapi.sqlalchemy.Serializer(models.Comment)

    api.add_model(user_serializer, sql_db)
    api.add_model(post_serializer, sql_db)
    api.add_model(comments_serializer, sql_db)
    return api


def create_app():
    """
    """
    app = flask.Flask(__name__)

    # *init_app* will register all api rules on the flask application.
    api = create_api()
    api.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
