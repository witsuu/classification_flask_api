import jwt
from utils.index import parse_json, jwt_key


def auth_verify(token):
    if not token:
        return None

    decode = jwt.decode(token, jwt_key(), algorithms=("HS256"))

    return parse_json(decode)
