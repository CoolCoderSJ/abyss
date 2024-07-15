import os
from appwrite.client import Client
from appwrite.services.users import Users
import sqlite3, json
from app import dict_factory

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    users = Users(client)

def list_users(queries=[]):
    if os.environ['DATABASE'] == "appwrite":
        return users.list(queries)['users']
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        q = []
        for query in queries:
            query = json.loads(query)
            q.append(f"{query['attribute']} {query['operator'].replace('equal', '=')} {query['values'][0]}")
        q = " AND ".join(q)
        r = cursor.execute(f"SELECT * FROM auth ?", (q,)).fetchall()
        conn.close()
        return r