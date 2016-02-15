#!/usr/bin/env python3

import jsonapi
import jsonapi.sqlalchemy

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative


# Create the sqlalchemy base, engine and the sessionmaker.
Base = sqlalchemy.ext.declarative.declarative_base()
engine = sqlalchemy.create_engine("sqlite:///example.db")

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)


class User(Base):

    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column("name", sqlalchemy.String(50))


class Post(Base):

    __tablename__ = "posts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.Text)

    author_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")
    )
    author = sqlalchemy.orm.relationship(
        "User", backref=sqlalchemy.orm.backref("posts")
    )


# Create the API and add the models.
db = jsonapi.sqlalchemy.Database(sessionmaker=Session)
api = jsonapi.base.api.API("/api", db)

user_schema = jsonapi.sqlalchemy.Schema(User)
post_schema = jsonapi.sqlalchemy.Schema(Post)

api.add_type(user_schema)
api.add_type(post_schema)
