from flask import render_template, session, abort, redirect, request, flash
from app import app, Query
from app import get_document, create_document, get_user, update_user, delete_document, get_all_docs, delete_user

from argon2 import PasswordHasher
ph = PasswordHasher()

@app.get("/settings")
def settings():
    if 'user' not in session:
        return redirect('/login')
    
    try:
        settings = get_document("data", 'settings', session['user'])
    except:
        settings = create_document("data", 'settings', session['user'], {
            "passwordHash": "",
            "disappearByDefault": False,
            "disablePage": False
        })
        
    user = get_user(session['user'])

    return render_template("settings.html", settings=settings, user=user)

@app.route("/settings/changePassword", methods=['POST'])
def change_password():
    if 'user' not in session:
        return redirect('/login')
    
    settings = get_document("data", 'settings', session['user'])
    user = get_user(session['user'])

    try:
        ph.verify(user['password'], request.form['old'])
    except:
        flash("Old password does not match the database.")
        return render_template("settings.html", **settings)
    
    if request.form['password'] != request.form['confirm']:
        flash("Passwords do not match.")
        return render_template("settings.html", **settings)
    
    try:
        update_user(user['$id'], user['email'], user['name'], request.form['password'])
    except Exception as e:
        flash(f"Failed to update password - {e}")
        return render_template("settings.html", **settings)
    
    flash("Password updated.")
    return redirect('/settings')

@app.route("/settings/updateDetails", methods=['POST'])
def change_details():
    if 'user' not in session:
        return redirect('/login')
    
    settings = get_document("data", 'settings', session['user'])
    user = get_user(session['user'])

    try: update_user(user['$id'], request.form['email'], request.form['name'], user['password'], updatePwd=False)
    except Exception as e:
        if str(e) != "A target with the same ID already exists.":
            flash(f"Failed to update - {e}")
            return render_template("settings.html", settings=settings, user=user)

    flash("Details updated.")
    return redirect('/settings')

@app.route("/settings/deleteAccount", methods=['POST'])
def delete_account():
    if 'user' not in session:
        return redirect('/login')
    
    settings = get_document("data", 'settings', session['user'])

    user = get_user(session['user'])
    
    delete_document("data", 'settings', session['user'])
    posts = get_all_docs("data", "posts", [Query.equal("uid", session['user'])])
    for post in posts:
        delete_document("data", "posts", post['$id'])

    try:
        delete_user(user['$id'])
    except Exception as e:
        print(e)
        flash("Failed to delete account.")
        return render_template("settings.html", settings=settings, user=user)
    
    session.clear()
    flash("Account deleted.")
    return redirect('/login')

@app.post("/settings/change")
def changeSettings():
    if 'user' not in session:
        return redirect('/login')
    
    passwordHash = request.form['passwordHash']
    disappearByDefault = True if 'disappearByDefault' in request.form else False
    disablePage = True if 'disablePage' in request.form else False

    hash = ph.hash(passwordHash) if passwordHash else ""

    try: 
        db.update_document("data", "settings", session['user'], {"disappearByDefault": disappearByDefault, "disablePage": disablePage})
    except:
        create_document("data", "settings", session['user'], {"disappearByDefault": disappearByDefault, "disablePage": disablePage})
    
    if "usepassw" in request.form and passwordHash:
        db.update_document("data", "settings", session['user'], {"passwordHash": hash})
    elif not "usepassw" in request.form:
        db.update_document("data", "settings", session['user'], {"passwordHash": ""})
    
    flash("Settings updated.")
    return redirect('/settings')