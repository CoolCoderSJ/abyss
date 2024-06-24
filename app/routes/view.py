from flask import render_template, session, abort, redirect, request, flash
from app import app, db, get_all_docs

@app.route("/view/<uid>")
def view_user(uid):
    settings = db.get_document("data", "settings", uid)
    if settings['passwordHash']:
        return render_template("password.html", uid=uid)

    posts = get_all_docs("data", "posts", [Query.equal("uid", uid)])
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
    return render_template("view.html", posts=posts)