#!/usr/bin/env python3

import asyncio

import mongoengine

import tornado
import tornado.httpserver
import tornado.platform.asyncio
import tornado.web

import jsonapi
import jsonapi.tornado
import jsonapi.mongoengine


class User(mongoengine.Document):

    email = mongoengine.EmailField()
    name = mongoengine.StringField()


class Post(mongoengine.Document):

    title = mongoengine.StringField()
    text = mongoengine.StringField()

    author = mongoengine.ReferenceField(User)


def create_api():
    api = jsonapi.tornado.TornadoAPI("/api")
    db = jsonapi.mongoengine.Database()

    user_serializer = jsonapi.mongoengine.Serializer(User)
    post_serializer = jsonapi.mongoengine.Serializer(Post)

    api.add_model(user_serializer, db)
    api.add_model(post_serializer, db)
    return api


def create_app():
    app = tornado.web.Application(autoreload=True, debug=True)

    api = create_api()
    api.init_app(app)
    return app


if __name__ == "__main__":
    tornado.platform.asyncio.AsyncIOMainLoop().install()

    mongoengine.connect()

    app = create_app()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(5000)

    ioloop = asyncio.get_event_loop()
    ioloop.run_forever()
