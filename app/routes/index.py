from flask import render_template, session, abort, redirect, request, flash
from app import app
from datetime import datetime
from cryptography.fernet import Fernet
import base64, os

from app import get_document, create_document, get_user

@app.route("/")
def index():
    if 'user' not in session:
        return render_template('landing.html')
    
    uid = session['user']
    try:
        settings = get_document("data", "settings", uid)
    except:
        settings = create_document("data", "settings", uid, {
            "passwordHash": "",
            "disappearByDefault": False,
            "disablePage": False
        })

    return render_template("index.html", settings=settings)

@app.post("/post")
def post_thought():
    if 'user' not in session:
        return redirect('/login')
    
    if not request.form or not 'thought' in request.form:
        flash("Please enter a thought.")
        return redirect('/')

    user = get_user(session['user'])
    key = base64.urlsafe_b64encode(user['password'].encode("utf-8").ljust(32)[:32])
    f = Fernet(key)

    create_document("data", "posts", "unique()", {"post": f.encrypt(request.form['thought'].encode("utf-8")).decode("utf-8"), "uid": session['user'], "postedAt": datetime.now().isoformat()})
    
    flash("Find peace knowing your thought is drifting away...")
    return redirect('/')