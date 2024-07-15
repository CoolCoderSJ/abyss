from flask import render_template, session, abort, redirect, request, flash
from app import app, Query
from cryptography.fernet import Fernet
import base64
from datetime import datetime
from argon2 import PasswordHasher
ph = PasswordHasher()

from app.utils import get_document, create_document, get_user, get_all_docs

@app.route("/view/<uid>")
def view_user(uid):
    try:
        settings = get_document("data", "settings", uid)
    except:
        settings = create_document("data", "settings", uid, {
            "passwordHash": "",
            "disappearByDefault": False,
            "disablePage": False
        })
    
    if settings['disablePage']:
        return render_template("disabled.html")

    if settings['passwordHash']:
        return render_template("password.html", uid=uid)

    posts = get_all_docs("data", "posts", [Query.equal("uid", uid)])
    posts.reverse()
    user = get_user(uid)
    key = base64.urlsafe_b64encode(user['password'].encode("utf-8").ljust(32)[:32])
    f = Fernet(key)
    for post in posts:
        post['post'] = f.decrypt(post['post'].encode("utf-8")).decode("utf-8").replace("\n", "<br>").replace("\r", "")
        post['postedAt'] = datetime.fromisoformat(post['postedAt']).strftime("%Y-%m-%d %I:%M %p")
    return render_template("view.html", posts=posts, name=user['name'])

@app.route("/view/<uid>/password", methods=['POST'])
def view_user_password(uid):
    settings = get_document("data", "settings", uid)

    if settings['disablePage']:
        return render_template("disabled.html")

    if not settings['passwordHash']:
        return redirect(f"/view/{uid}")

    try: 
        ph.verify(settings['passwordHash'], request.form['password'])
    except:
        flash("Invalid password.")
        return render_template("password.html", uid=uid)

    posts = get_all_docs("data", "posts", [Query.equal("uid", uid)])
    posts.reverse()
    user = get_user(uid)
    key = base64.urlsafe_b64encode(user['password'].encode("utf-8").ljust(32)[:32])
    f = Fernet(key)
    for post in posts:
        post['post'] = f.decrypt(post['post'].encode("utf-8")).decode("utf-8").replace("\n", "<br>").replace("\r", "")
        post['postedAt'] = datetime.fromisoformat(post['postedAt']).strftime("%Y-%m-%d %I:%M %p")
    return render_template("view.html", posts=posts, name=user['name'])