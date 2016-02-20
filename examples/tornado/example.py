#!/usr/bin/env python3

import asyncio

import tornado
import tornado.gen
import tornado.ioloop
import tornado.platform
import tornado.httpserver

import motorengine

import jsonapi
import jsonapi.motorengine
import jsonapi.tornado


class User(motorengine.Document):

    name = motorengine.StringField()
    email = motorengine.EmailField()

    @jsonapi.marker.method.attribute()
    def greetings_earthling(self):
        return "Greetings, earthling {}!".format(self.name)


class Post(motorengine.Document):

    text = motorengine.StringField()
    author = motorengine.ReferenceField(User)


def create_api():
    """
    Creates the py-jsonapi api object.
    """
    # Use the motorengine schema for the models.
    user_schema = jsonapi.motorengine.Schema(User)
    post_schema = jsonapi.motorengine.Schema(Post)

    # Create the motorengine database adapter.
    db = jsonapi.motorengine.Database()

    # Create the API
    api = jsonapi.tornado.TornadoAPI("/api", db)
    api.add_type(user_schema)
    api.add_type(post_schema)
    return api


def create_app():
    """
    Creates the tornado application.
    """
    app = tornado.web.Application(autoreload=True, debug=True)

    api = create_api()
    api.init_app(app)
    return app


if __name__ == "__main__":
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app = create_app()
    motorengine.connect("py-jsonapi-test")

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(5000)

    loop = asyncio.get_event_loop()
    loop.run_forever()
