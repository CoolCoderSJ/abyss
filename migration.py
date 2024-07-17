# this is only to migrate to the enw encryption system. Not to be used otherwise.

import os
from dotenv import load_dotenv
load_dotenv()

from uuid import uuid4

from cryptography.fernet import Fernet
import base64

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.services.users import Users

client = Client()
client.set_endpoint(os.environ['APPWRITE_HOST'])
client.set_project(os.environ['APPWRITE_ID'])
client.set_key(os.environ['APPWRITE_KEY'])

db = Databases(client)
users = Users(client)

def get_all_docs(data, collection, queries=[]):
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


u = users.list()['users']
for user in u:
    uid = user['$id']
    upwd = user['password']

    uuidkey = str(uuid4())

    key = base64.urlsafe_b64encode(upwd.encode("utf-8").ljust(32)[:32])
    f = Fernet(key)
    key = f.encrypt(uuidkey.encode("utf-8")).decode("utf-8")
    
    pwdkey = base64.urlsafe_b64encode(upwd.encode("utf-8").ljust(32)[:32])
    f2 = Fernet(pwdkey)

    db.update_document("data", "settings", uid, {"encryptionKey": key})

    posts = get_all_docs("data", "posts", [Query.equal("uid", uid)])
    for post in posts:
        pid = post['$id']
        post = f2.decrypt(post['post'].encode("utf-8")).decode("utf-8")
        post = f.encrypt(post.encode("utf-8")).decode("utf-8")
        db.update_document("data", "posts", pid, {"post": post})
        print(f"Updated post {pid}")

    print(f"Updated user {uid}")