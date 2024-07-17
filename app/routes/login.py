from flask import render_template, session, abort, redirect, request, flash
from app import app, Query
from app.utils import list_users, create_user, create_document
import os

from argon2 import PasswordHasher
ph = PasswordHasher()
from uuid import uuid4
from cryptography.fernet import Fernet
import base64

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
        if os.environ['ALLOW_SIGNUPS'] == "false" or os.environ['SINGLE_USER'] == "true":
            flash("Signups are disabled.")
            return render_template("login.html")
        
        user = create_user(email, email.split("@")[0], password)
        u = str(uuid4())
        key = base64.urlsafe_b64encode(user['password'].encode("utf-8").ljust(32)[:32])
        f = Fernet(key)
        key = f.encrypt(u.encode("utf-8")).decode("utf-8")
        create_document("data", "settings", user['$id'], {
            "passwordHash": "",
            "disappearByDefault": False,
            "disablePage": False,
            "encryptionKey": key
        })
        sessid = user['$id']
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