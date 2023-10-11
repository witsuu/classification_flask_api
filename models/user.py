import datetime as dt
from marshmallow import Schema, fields
from db import get_db


class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.created_at = dt.datetime.now()
        self.updated_at = dt.datetime.now()

    def __repr__(self):
        return "<User(username={self.username!r})>".format(self=self)


UserSchema = Schema.from_dict(
    {"username": fields.Str(required=True, error_messages={"required": "username is required"}),
     "email": fields.Email(required=True, error_messages={"required": "email is required"}),
     "password": fields.Str(required=True, error_messages={"required": "password is required"}),
     "created_at": fields.DateTime(),
     "updated_at": fields.DateTime()
     }
)


def get_user_collection():
    return get_db().get_collection("Users")


def get_all_user():
    return get_db().get_collection("Users").find()
