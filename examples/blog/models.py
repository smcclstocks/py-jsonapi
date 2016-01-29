#!/usr/bin/env python3

# std
import datetime

# third party
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm


Base = sqlalchemy.ext.declarative.declarative_base()


class User(Base):

    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    email = sqlalchemy.Column("email", sqlalchemy.String(50))
    date_added = sqlalchemy.Column(
        "date_added", sqlalchemy.DateTime(),
        default=datetime.datetime.utcnow
    )


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

    comment_ids = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("comments.id")
    )
    comments = sqlalchemy.orm.relationship(
        "Comment", backref=sqlalchemy.orm.backref("post")
    )


class Comment(Base):

    __tablename__ = "comments"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.Text)

    author_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")
    )
    author = sqlalchemy.orm.relationship(
        "User", backref=sqlalchemy.orm.backref("comments")
    )
