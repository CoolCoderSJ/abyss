import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
import sqlite3, json
from app import dict_factory

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    db = Databases(client)
    
def get_all_docs(data, collection, queries=[]):
    if os.environ['DATABASE'] == "appwrite":
        docs = []
        offset = 0
        while True:
            try: 
                queries.remove(Query.offset(offset))
                queries.remove(Query.limit(100))
            except:
                break
        queries.append(Query.offset(offset))
        queries.append(Query.limit(100))
        print(queries)
        while True:
            results = db.list_documents(data, collection, queries=queries)
            if len(docs) == results['total']:
                break
            results = results['documents']
            docs += results
            offset += len(results)
        return docs

    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        conn.row_factory = dict_factory
        r = cursor.execute(f"SELECT * FROM {collection} WHERE ? = ?", (json.loads(queries[0])['attribute']), json.loads(queries[0])['values'][0]).fetchall()
        conn.commit()
        conn.close()
        for i in r:
            try: i['$id'] = i['id']
            except: i['$id'] = i['uid']
        return r