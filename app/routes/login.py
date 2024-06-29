from flask import render_template, session, abort, redirect, request, flash
from app import app, db, get_all_docs, users, Query

from argon2 import PasswordHasher
ph = PasswordHasher()

@app.get("/login")
def login():
    if 'user' in session:
        return redirect('/')
    return render_template("login.html")

@app.post("/login")
def login_post():
    if 'user' in session:
        return redirect('/')
    
    if not request.form or not 'email' in request.form or not 'password' in request.form:
        flash("Please enter your email and password.")
        return render_template("login.html")
    
    email = request.form['email']
    password = request.form['password']

    allusers = users.list(queries=[Query.equal('email', email)])['users']
    if len(allusers) == 0:
        sessid = users.create_argon2_user('unique()', email=email, name=email.split("@")[0], password=password)['$id']
        session['user'] = sessid
        return redirect("/")
    
    user = allusers[0]
    try:
        ph.verify(user['password'], password)
    except: 
        flash("Invalid password.")
        return render_template("login.html")
   
    session['user'] = user['$id']
    return redirect("/")