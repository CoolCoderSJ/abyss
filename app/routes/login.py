from flask import render_template, session, abort, redirect, request, flash
from app import app, Query
from app.utils import list_users, create_user

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

    allusers = list_users([Query.equal("email", email)])
    if len(allusers) == 0:
        sessid = create_user(email, email.split("@")[0], password)['$id']
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