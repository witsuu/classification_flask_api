import pandas as pd
import json
from flask import Flask, jsonify, request, make_response
from bson import json_util
import bcrypt
import jwt

from db import get_db
from validations.register import register
from validations.login import login
from models.user import User, UserSchema, get_all_user, get_user_collection

app = Flask(__name__)
db = get_db()
dataFrame = pd.read_csv("./dataset/titanic.csv")

app.secret_key = "dfdb692dc1b49fdb1d109de8741d357a9255ff101f6cf10ac42366e0a221650f"


def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route("/")
def App():
    users = get_all_user()

    return parse_json(users)


@app.route("/get-data")
def getData():
    return jsonify({"status": "success", "data": dataFrame.to_dict()})


@app.route("/get-columns-values")
def getColumnsValues():
    head = list(dataFrame.columns.values)
    return jsonify({
        "status": "success",
        "data": head
    }), 200


@app.post("/login")
def login_post():
    result = login(request.json)

    if (result['error']):
        return result['error'], 400

    user = get_user_collection().find_one({"email": result['data']['email']})
    if not user:
        return {
            "email": ["Email not found"]
        }, 400

    bytes = result["data"]["password"].encode("utf-8")
    passCheck = bcrypt.checkpw(bytes, user['password'].encode("utf-8"))
    if not passCheck:
        return {
            "password": ["password do not match"]
        }, 400

    jwt_encode = jwt.encode(
        {"id": parse_json(user['_id'])}, app.secret_key, algorithm=("HS256"))

    jwt_split = jwt_encode.split(".")

    res = make_response({"message": "Login succesfully"})
    res.set_cookie("hd", jwt_split[0], secure=True)
    res.set_cookie("py", jwt_split[1], secure=True)
    res.set_cookie("sg", jwt_split[2], secure=True, httponly=True)

    return res


@app.post("/store-user")
def storeUser():
    result = register(request.json)

    if (result['error']):
        return result['error'], 400

    usernameExist = get_user_collection().find_one(
        {"username": result["data"]['username']})
    if (usernameExist):
        return {
            "username": ["username already in use"]
        }, 400

    emailExist = get_user_collection().find_one(
        {"email": result["data"]['email']})
    if (emailExist):
        return {
            "email": ["Email already in use"]
        }, 400

    passBytes = result["data"]["password"].encode("utf-8")
    salt = bcrypt.gensalt()
    passwordHash = bcrypt.hashpw(passBytes, salt)

    try:
        user = User(result['data']["username"], result["data"]
                    ["email"], passwordHash)
        schema = UserSchema()
        get_user_collection().insert_one(schema.dump(user))

        return jsonify({"message": "User added successfully", "status": "success"}), 200
    except NameError as Error:
        return jsonify({
            "message": Error,
            "status": "error"
        }), 400
