from flask import render_template, session, abort, redirect, request, flash
from app import app, db, get_all_docs
from datetime import datetime

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
    
    db.create_document("data", "posts", {"thought": request.form['thought'], "uid": session['user'], "postedAt": datetime.now().isoformat()})
    
    flash("Find peace knowing your thought is drifting away...")
    return redirect('/')