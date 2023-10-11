from models.user import UserSchema
from marshmallow import ValidationError


def register(data):
    try:
        result = UserSchema().load(data)

        return {"data": result, 'error': None}
    except ValidationError as err:
        return {"error": err.messages, 'data': None}
