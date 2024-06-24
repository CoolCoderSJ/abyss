from flask import render_template, session, abort, redirect, request, flash
from app import app, db, get_all_docs, users

from argon2 import PasswordHasher
ph = PasswordHasher()

@app.get("/settings")
def settings():
    if 'user' not in session:
        return redirect('/login')
    
    settings = db.get_document("data", 'settings', session['user'])
    
    return render_template("settings.html", kwargs=settings)

@app.route("/settings/changePassword", methods=['POST'])
def change_password():
    if 'user' not in session:
        return redirect('/login')
    
    settings = db.get_document("data", 'settings', session['user'])
    
    if request.form['password'] != request.form['confirm']:
        flash("Passwords do not match.")
        return render_template("settings.html", kwargs=settings)
    
    user = users.get(session['user'])
    
    if not users.update_user(user['$id'], password=request.form['password']):
        flash("Failed to update password.")
        return render_template("settings.html", kwargs=settings)
    
    flash("Password updated.")
    return redirect('/settings')

@app.route("/settings/updateDetails", methods=['POST'])
def change_details():
    if 'user' not in session:
        return redirect('/login')
    
    settings = db.get_document("data", 'settings', session['user'])
    
    user = users.get(session['user'])

    if not users.update_email(user['$id'], email=request.form['email']):
        flash("Failed to update email.")
        return render_template("settings.html", kwargs=settings)

    if not users.update_name(user['$id'], name=request.form['name']):
        flash("Failed to update name.")
        return render_template("settings.html", kwargs=settings)
    
    flash("Details updated.")
    return redirect('/settings')

@app.route("/settings/deleteAccount", methods=['POST'])
def delete_account():
    if 'user' not in session:
        return redirect('/login')
    
    settings = db.get_document("data", 'settings', session['user'])
    
    user = users.get(session['user'])
    
    if not users.delete(user['$id']):
        flash("Failed to delete account.")
        return render_template("settings.html", kwargs=settings)
    
    db.delete_document("data", 'settings', session['user'])

    session.clear()
    flash("Account deleted.")
    return redirect('/login')

@app.post("/settings/change")
def changeSettings():
    if 'user' not in session:
        return redirect('/login')
        
    password = request.form['password']
    disappearByDefault = True if request.form['disappearByDefault'] == "on" else False

    hash = ph.hash(password)

    try: 
        db.update_document("data", "settings", session['user'], {"passwordHash": hash, "disappearByDefault": disappearByDefault})
    except:
        db.create_document("data", "settings", session['user'], {"passwordHash": hash, "disappearByDefault": disappearByDefault})
    
    flash("Settings updated.")
    return redirect('/settings')