#!/usr/bin/env python3

import mongoengine
import flask
import jsonapi, jsonapi.mongoengine, jsonapi.flask

class User(mongoengine.Document):
    name = mongoengine.StringField()
    email = mongoengine.EmailField()
    birthday = mongoengine.DateTimeField()

app = flask.Flask(__name__)

db = jsonapi.mongoengine.Database()
api = jsonapi.flask.FlaskAPI(uri="/api", db=db, flask_app=app)

user_schema = jsonapi.mongoengine.Schema(User)
api.add_type(user_schema)

if __name__ == "__main__":
    mongoengine.connect("py_jsonapi")
    app.run(debug=True)
