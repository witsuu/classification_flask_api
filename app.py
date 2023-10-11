import pandas as pd
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import bcrypt
import jwt
import os
from utils.index import parse_json, jwt_key

from db import get_db
from validations.register import register
from validations.login import login
from models.user import User, UserSchema, get_all_user, get_user_collection
from middlewares import auth

app = Flask(__name__)
CORS(app, supports_credentials=True)

db = get_db()
dataFrame = pd.read_csv("./dataset/titanic.csv")

app.secret_key = "dfdb692dc1b49fdb1d109de8741d357a9255ff101f6cf10ac42366e0a221650f"


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
        {"id": parse_json(user['_id'])}, jwt_key(), algorithm=("HS256"))

    jwt_split = jwt_encode.split(".")

    user = get_user_collection().find_one(
        {"email": result['data']['email']}, {"password": False})

    res = make_response(parse_json(user))
    res.set_cookie("hd", jwt_split[0], secure=True, samesite='None')
    res.set_cookie("pl", jwt_split[1], secure=True, samesite='None')
    res.set_cookie("sg", jwt_split[2], secure=True,
                   httponly=True, samesite='None')

    return res


@app.get("/logged-in")
def logged_in():
    if not request.cookies:
        return jsonify({"message": "Unauthorized", "code": 401}), 401

    tokenList = [request.cookies.get("hd"), request.cookies.get(
        "pl"), request.cookies.get("sg")]

    token = ".".join(tokenList)

    is_logged = auth.auth_verify(token)

    if not is_logged:
        return jsonify({"message": "Unauthorized", "code": 401}), 401
    else:
        return jsonify({"message": "Authorized", "code": 200}), 200


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


@app.post("/logout")
def logout_post():
    res = make_response({"message": "logout succesfully"})
    res.delete_cookie("hd", path="/", secure=True, samesite="None")
    res.delete_cookie("pl", path="/", secure=True, samesite="None")
    res.delete_cookie("sg", path="/", secure=True, samesite="None")

    return res
