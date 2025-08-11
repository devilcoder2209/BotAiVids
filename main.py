import os
import uuid
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import app, db, login_manager, User
from generate_process import text_to_speech, create_reel

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not username or not email or not password or not confirm:
            flash("All fields are required.", "danger")
            return redirect(url_for("signup"))
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("signup"))
        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Signup successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        try:
            rec_id = request.form.get("uuid")
            desc = request.form.get("text")
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            input_files = []
            files = request.files.getlist("files")
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(upload_path, filename))
                    input_files.append(filename)
            # Save description
            with open(os.path.join(upload_path, "description.txt"), "w") as desc_file:
                desc_file.write(desc)
            # Write input.txt
            with open(os.path.join(upload_path, "input.txt"), "w") as fl:
                for f in input_files:
                    fl.write(f"file '{f}'\nduration 1\n")
            # Call processing functions
            try:
                text_to_speech(rec_id)
                create_reel(rec_id)
            except Exception as e:
                print(f"[ERROR] Processing failed for {rec_id}: {e}")
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels = os.listdir("static/reels") if os.path.exists("static/reels") else []
    return render_template("gallery.html", reels=reels)


