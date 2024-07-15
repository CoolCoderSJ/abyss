import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.query import Query
import sqlite3, shortuuid, json
from app import dict_factory
from argon2 import PasswordHasher
ph = PasswordHasher()

if os.environ['DATABASE'] == "appwrite":
    client = Client()
    client.set_endpoint(os.environ['APPWRITE_HOST'])
    client.set_project(os.environ['APPWRITE_ID'])
    client.set_key(os.environ['APPWRITE_KEY'])
    db = Databases(client)
    users = Users(client)

def create_document(database, collection, document_id, data):
    if os.environ['DATABASE'] == "appwrite":
        return db.create_document(database, collection, document_id, data)
    elif os.environ['DATABASE'] == "sqlite":
        if document_id == "unique()":
            document_id = shortuuid.uuid()
        conn = sqlite3.connect("data.db")
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        if collection == "settings" and "uid" not in data.keys():
            data['uid'] = document_id

        if collection == "posts":
            order = ['uid', 'post', 'postedAt', 'hidden']
        elif collection == "settings":
            order = ['uid', 'passwordHash', 'disappearByDefault', 'disablePage']

        d = [document_id] if collection == "posts" else []
        data = {k: data[k] for k in order if k in data.keys()}
        d.extend(data.values())
        d = tuple(d)
        uidStr = "uid" if collection == "settings" else "id"
        print(uidStr, d)
        cursor.execute(f"INSERT INTO {collection} VALUES ({', '.join(['?']*len(d))})", d)
        conn.commit()
        r = cursor.execute(f"SELECT * FROM {collection} WHERE {uidStr} = ?", (document_id,)).fetchone()
        conn.close()
        print(r)
        r['$id'] = r[uidStr]
        return r

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
    
def delete_document(database, collection, document_id):
    if os.environ['DATABASE'] == "appwrite":
        return db.delete_document(database, collection, document_id)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {collection} WHERE ? = ?", ("uid" if collection == "settings" else "id", document_id))
        conn.commit()
        conn.close()
        return True
    
def delete_user(uid):
    if os.environ['DATABASE'] == "appwrite":
        return users.delete(uid)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM auth WHERE uid = ?", (uid,))
        conn.commit()
        conn.close()
        return True


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
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        print((json.loads(queries[0])['attribute'], json.loads(queries[0])['values'][0]))
        r = cursor.execute(f"SELECT * FROM {collection} WHERE {json.loads(queries[0])['attribute']} = ?", (json.loads(queries[0])['values'][0],)).fetchall()
        conn.close()
        for i in r:
            try: i['$id'] = i['id']
            except: i['$id'] = i['uid']
        return r

def get_document(database, collection, document_id):
    if os.environ['DATABASE'] == "appwrite":
        return db.get_document(database, collection, document_id)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        uidStr = "id" if collection == "posts" else "uid"
        res = cursor.execute(f"SELECT * FROM {collection} WHERE {uidStr} = ?", (document_id,)).fetchone()
        conn.close()
        res['$id'] = res[uidStr]
        return res

def get_user(userId):
    if os.environ['DATABASE'] == "appwrite":
        return users.get(userId)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        r = cursor.execute(f"SELECT * FROM auth WHERE uid = ?", (userId,)).fetchone()
        conn.close()
        print(r)
        r['$id'] = r['uid']
        return r

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
            print(query)
            q.append(f"WHERE {query['attribute']} {query['method'].replace('equal', '=')} ?")
        q = " AND ".join(q)
        print(q)
        r = cursor.execute(f"SELECT * FROM auth {q}", (query['values'][0],)).fetchall()
        conn.close()
        for i in r:
            i['$id'] = i['uid']
        return r

def update_document(database, collection, document_id, data):
    if os.environ['DATABASE'] == "appwrite":
        return db.update_document(database, collection, document_id, data)
    elif os.environ['DATABASE'] == "sqlite":
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        set = ', '.join([f"{k} = ?" for k in data.keys()])
        uidStr = "id" if collection == "posts" else "uid"

        if collection == "posts":
            order = ['uid', 'post', 'postedAt', 'hidden']
        elif collection == "settings":
            order = ['uid', 'passwordHash', 'disappearByDefault', 'disablePage']

        data = {k: data[k] for k in order if k in data.keys()}

        d = list(data.values())
        d.append(document_id)
        d = tuple(d)
        
        cursor.execute(f"UPDATE {collection} SET {set} WHERE {uidStr} = ?", d)
        conn.commit()
        conn.close()
        return True

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