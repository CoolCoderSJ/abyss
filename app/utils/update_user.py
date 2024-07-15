import os
from appwrite.client import Client
from appwrite.services.users import Users
import sqlite3
from app import dict_factory
from argon2 import PasswordHasher
ph = PasswordHasher()

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    users = Users(client)

def update_user(uid, email, name, password, updatePwd=True):
    if os.environ['DATABASE'] == "appwrite":
        if updatePwd: users.update_password(uid, password)
        users.update_name(uid, name)
        return users.update_email(uid, email)
    elif os.environ['DATABASE'] == "sqlite":
        if updatePwd: password = ph.hash(password)
        conn = sqlite3.connect("data.db")
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("UPDATE auth SET email = ?, name = ?, password = ? WHERE uid = ?", (email, name, password, uid))
        conn.commit()
        r = cursor.execute(f"SELECT * FROM auth WHERE uid = ?", (uid,)).fetchone()
        conn.close()
        r['$id'] = r['uid']
        return r