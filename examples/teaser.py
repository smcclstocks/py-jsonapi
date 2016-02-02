#!/usr/bin/env python3

import mongoengine
import flask
import jsonapi, jsonapi.mongoengine, jsonapi.flask

app = flask.Flask(__name__)
api = jsonapi.flask.FlaskAPI("/api", flask_app=app)

class User(mongoengine.Document):
    name = mongoengine.StringField()
    email = mongoengine.EmailField()
    birthday = mongoengine.DateTimeField()

mongoengine_adapter = jsonapi.mongoengine.Database()
user_schema = jsonapi.mongoengine.Schema(User)
api.add_type(user_schema, mongoengine_adapter)

if __name__ == "__main__":
    mongoengine.connect("py_jsonapi")
    app.run(debug=True)
