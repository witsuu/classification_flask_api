import json
from bson import json_util


def parse_json(data):
    return json.loads(json_util.dumps(data))


def jwt_key():
    return "2f5d857786b480548e73daccfac22d93e7e96bcaf00f4b84156f8146ec0cf4fe"
