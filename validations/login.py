from models.user import UserSchema
from marshmallow import ValidationError


def login(data):
    try:
        result = UserSchema().load(data, partial=("username",))

        return {"data": result, 'error': None}
    except ValidationError as err:
        return {"error": err.messages, 'data': None}
