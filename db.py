from pymongo import MongoClient


def get_db():
    client = MongoClient(
        "mongodb+srv://cakwit_flask:witsudy217@cluster0.7jfgyzb.mongodb.net/?retryWrites=true&w=majority")

    db = client.get_database("classification")

    return db
