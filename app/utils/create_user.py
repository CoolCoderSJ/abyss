import os
from appwrite.client import Client
from appwrite.services.users import Users
import sqlite3, shortuuid
from app import dict_factory
from argon2 import PasswordHasher
ph = PasswordHasher()

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    users = Users(client)

def create_user(email, name, password):
    if os.environ['DATABASE'] == "appwrite":
        return users.create_argon2_user('unique()', email=email, name=name, password=password)
    elif os.environ['DATABASE'] == "sqlite":
        password = ph.hash(password)
        conn = sqlite3.connect("data.db")
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        uid = shortuuid.uuid()
        cursor.execute("INSERT INTO auth VALUES (?, ?, ?, ?)", (uid, email, name, password))
        conn.commit()
        r = cursor.execute(f"SELECT * FROM auth WHERE uid = ?", (uid,)).fetchone()
        conn.close()
        r['$id'] = r['uid']
        return r