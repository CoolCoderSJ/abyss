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

client2 = Client()
client2.set_endpoint("https://ab.shuchir.dev/v1")
client2.set_project(os.environ['APPWRITE_ID'])
client2.set_key(os.environ['APPWRITE_KEY'])

db = Databases(client)
users = Users(client)

db2 = Databases(client2)

def get_all_docs(db, data, collection, queries=[]):
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

    key = base64.urlsafe_b64encode(uuidkey.encode("utf-8").ljust(32)[:32])
    f = Fernet(key)

    pwdkey = base64.urlsafe_b64encode(upwd.encode("utf-8").ljust(32)[:32])
    f2 = Fernet(pwdkey)

    encKey = f2.encrypt(uuidkey.encode("utf-8")).decode("utf-8")
    db.update_document("data", "settings", uid, {"encryptionKey": encKey})

    posts = get_all_docs(db, "data", "posts", [Query.equal("uid", uid)])
    for post in posts:
        pid = post['$id']
        post = f2.decrypt(post['post'].encode("utf-8")).decode("utf-8")
        post = f.encrypt(post.encode("utf-8")).decode("utf-8")
        db.update_document("data", "posts", pid, {"post": post})
        print(f"Updated post {pid}")

    print(f"Updated user {uid}")

# posts2 = get_all_docs(db2, "data", "posts")
# for post in posts2:
#     pid = post['$id']
#     post = post['post']
    
#     try: 
#         db.update_document("data", "posts", pid, {"post": post})
#         print(f"Updated post {pid}")
#     except: pass