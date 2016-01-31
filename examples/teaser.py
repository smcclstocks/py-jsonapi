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
user_serializer = jsonapi.mongoengine.Serializer(User)
api.add_model(user_serializer, mongoengine_adapter)

if __name__ == "__main__":
    mongoengine.connect("py_jsonapi")
    app.run(debug=True)
