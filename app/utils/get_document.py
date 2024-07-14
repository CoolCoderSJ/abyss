import os
from appwrite.client import Client
from appwrite.services.databases import Databases
import sqlite3

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    db = Databases(client)

def get_document(database, collection, document_id):
    if os.environ['DATABASE'] == "appwrite":
        return db.get_document(database, collection, document_id)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        res = cursor.execute(f"SELECT * FROM {collection} WHERE uid = ?", (document_id,)).fetchone()
        conn.close()
        return res