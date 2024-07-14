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

def create_document(database, collection, document_id, data):
    if os.environ['DATABASE'] == "appwrite":
        return db.create_document(database, collection, document_id, data)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        d = [document_id]
        d.extend(data.values())
        d = tuple(d)
        cursor.execute(f"INSERT INTO {collection} VALUES ({', '.join(['?']*len(d))})", d)
        conn.commit()
        conn.close()
        return True