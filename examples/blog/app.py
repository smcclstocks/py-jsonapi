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

engine = sqlalchemy.create_engine("sqlite:////tmp/blog")#+datetime.datetime.utcnow().ctime())

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)


class User(Base):

    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column("name", sqlalchemy.String(50), nullable=False)

    @jsonapi.marker.method.attribute()
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

    user_schema = jsonapi.sqlalchemy.Schema(User)
    post_schema = jsonapi.sqlalchemy.Schema(Post)
    comment_schema = jsonapi.sqlalchemy.Schema(Comment)

    sql_db = jsonapi.sqlalchemy.Database(sessionmaker=Session)

    api.add_type(user_schema, sql_db)
    api.add_type(post_schema, sql_db)
    api.add_type(comment_schema, sql_db)
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
    app.run(debug=True)
