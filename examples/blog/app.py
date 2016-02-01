#!/usr/bin/env python3

# NOTE:
#
#   Make sure to update the documentation if you edit this file.
#

import datetime

import flask
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import jsonapi
import jsonapi.flask
import jsonapi.sqlalchemy


# Models
# ------

Base = sqlalchemy.ext.declarative.declarative_base()

engine = sqlalchemy.create_engine("sqlite://")

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)


class User(Base):

    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column("name", sqlalchemy.String(50), nullable=False)

    @jsonapi.marker.method.Attribute()
    def first_name(self):
        return self.name.split()[0]


class Post(Base):

    __tablename__ = "posts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    author_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")
    )
    author = sqlalchemy.orm.relationship(
        "User", backref=sqlalchemy.orm.backref("posts")
    )


class Comment(Base):

    __tablename__ = "comments"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    author_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")
    )
    author = sqlalchemy.orm.relationship(
        "User", backref=sqlalchemy.orm.backref("comments")
    )

    post_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id")
    )
    post = sqlalchemy.orm.relationship(
        "Post", backref=sqlalchemy.orm.backref("comments")
    )

# Application
# -----------

def create_api():
    """
    Creates the JSONapi.
    """
    api = jsonapi.flask.FlaskAPI("/api")

    user_serializer = jsonapi.sqlalchemy.Serializer(User)
    post_serializer = jsonapi.sqlalchemy.Serializer(Post)
    comment_serializer = jsonapi.sqlalchemy.Serializer(Comment)

    sql_db = jsonapi.sqlalchemy.Database(sessionmaker=Session)

    api.add_model(user_serializer, sql_db)
    api.add_model(post_serializer, sql_db)
    api.add_model(comment_serializer, sql_db)
    return api


def create_app():
    """
    Creates the flask application.
    """
    app = flask.Flask(__name__)

    api = create_api()
    api.init_app(app)

    Base.metadata.create_all(engine)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
