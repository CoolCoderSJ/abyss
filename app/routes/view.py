from flask import render_template, session, abort, redirect, request, flash
from app import app, db, get_all_docs, users
from cryptography.fernet import Fernet

@app.route("/view/<uid>")
def view_user(uid):
    try:
        settings = db.get_document("data", "settings", uid)
    except:
        settings = db.create_document("data", "settings", uid, {
            "passwordHash": "",
            "disappearByDefault": False,
            "disablePage": False
        })
    
    if settings['disablePage']:
        return render_template("disabled.html")

    if settings['passwordHash']:
        return render_template("password.html", uid=uid)

    posts = get_all_docs("data", "posts", [Query.equal("uid", uid)])
    user = users.get(uid)
    f = Fernet(user['password'])
    for post in posts:
        post['thought'] = f.decrypt(post['thought'].encode("utf-8")).decode("utf-8")
    return render_template("view.html", posts=posts)

@app.route("/view/<uid>/password", methods=['POST'])
def view_user_password(uid):
    settings = db.get_document("data", "settings", uid)
    if not settings['passwordHash']:
        return redirect(f"/view/{uid}")

    if not ph.verify(settings['passwordHash'], request.form['password']):
        flash("Invalid password.")
        return render_template("password.html", uid=uid)

    posts = get_all_docs("data", "posts", [Query.equal("uid", uid)])
    user = users.get(uid)
    f = Fernet(user['password'])
    for post in posts:
        post['thought'] = f.decrypt(post['thought'].encode("utf-8")).decode("utf-8")
    return render_template("view.html", posts=posts)