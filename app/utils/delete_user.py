import os
from appwrite.client import Client
from appwrite.services.users import Users
import sqlite3, shortuuid

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    users = Users(client)

def delete_user(uid):
    if os.environ['DATABASE'] == "appwrite":
        return users.delete(uid)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM auth WHERE uid = ?", (uid))
        conn.commit()
        conn.close()
        return True