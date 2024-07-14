import os
from appwrite.client import Client
from appwrite.services.users import Users
import sqlite3
from app import dict_factory

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    users = Users(client)

def get_user(database, collection, userId):
    if os.environ['DATABASE'] == "appwrite":
        return users.get(userId)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        r = cursor.execute(f"SELECT * FROM auth WHERE uid = ?", (userId,)).fetchone()
        conn.close()
        return r