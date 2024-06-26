from flask import render_template, session, abort, redirect, request, flash
from app import app, db, get_all_docs, users
from datetime import datetime
from cryptography.fernet import Fernet

@app.route("/")
def index():
    if 'user' not in session:
        return render_template('landing.html')
    
    return render_template("index.html")

@app.post("/post")
def post_thought():
    if 'user' not in session:
        return redirect('/login')
    
    if not request.form or not 'thought' in request.form:
        flash("Please enter a thought.")
        return redirect('/')

    user = users.get(session['user'])
    f = Fernet(user['password'])

    db.create_document("data", "posts", {"thought": f.encrypt(request.form['thought'].encode("utf-8")).decode("utf-8"), "uid": session['user'], "postedAt": datetime.now().isoformat()})
    
    flash("Find peace knowing your thought is drifting away...")
    return redirect('/')