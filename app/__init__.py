from flask import Flask, session, request, redirect
from flask_session import Session

from dotenv import load_dotenv
import os 

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.services.users import Users

import sqlite3

load_dotenv()

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    db = Databases(client)
    users = Users(client)

    res = db.list()
    if res['total'] == 0:
        print("Creating database...")
        db.create("data", "data")

        print("Creating collections...")
        db.create_collection("data", "posts", "posts")
        db.create_collection("data", "settings", "settings")

        print("Creating attributes...")
        db.create_string_attribute("data", "posts", key="uid", size=99, required=False)
        db.create_string_attribute("data", "posts", key="post", size=9999, required=False)
        db.create_datetime_attribute("data", "posts", key="postedAt", required=False)
        db.create_boolean_attribute("data", "posts", key="hidden", required=False)

        db.create_string_attribute("data", "settings", key="passwordHash", size=99, required=False)
        db.create_boolean_attribute("data", "settings", key="disappearByDefault", required=False)
        db.create_boolean_attribute("data", "settings", key="disablePage", required=False)

        print("Database created.")

elif os.environ['DATABASE'] == "sqlite":
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    rows = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth';").fetchall()
    print(rows)

    if len(rows) == 0:
        cursor.execute("CREATE TABLE auth (uid TEXT PRIMARY KEY, email TEXT, name TEXT, password TEXT);")
        cursor.execute("CREATE TABLE posts (id TEXT PRIMARY KEY, uid TEXT, post TEXT, postedAt TEXT, hidden INTEGER);")
        cursor.execute("CREATE TABLE settings (uid TEXT PRIMARY KEY, passwordHash TEXT, disappearByDefault INTEGER, disablePage INTEGER);")
        conn.commit()

    conn.close()

db, users = None, None

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem" 
app.config["SECRET_KEY"] = os.environ['SECRET_KEY']
app.config["SESSION_PERMANENT"] = True
Session(app)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

from .utils import *
from .routes import *