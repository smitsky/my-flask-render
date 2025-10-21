from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Change for production!
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=5)

# DYNAMIC DB: Postgres on Render, SQLite local
db_url = os.getenv('DATABASE_URL', 'sqlite:///users.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100))

    def __init__(self, name, email=""):
        self.name = name
        self.email = email

# Routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        user = User.query.filter_by(name=name).first()
        if not user:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()
        session["user"] = name
        flash("Login successful!")
        return redirect(url_for("user"))
    return render_template("login.html")

@app.route('/user', methods=["GET", "POST"])
def user():
    if "user" not in session:
        flash("Please log in!")
        return redirect(url_for("login"))
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(name=session["user"]).first()
        user.email = email
        db.session.commit()
        flash("Email saved!")
    return render_template("user.html", email=User.query.filter_by(name=session["user"]).first().email)

@app.route('/view')
def view():
    users = User.query.all()
    return render_template("view.html", users=users)

@app.route('/delete/<int:id>')
def delete(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted!")
    return redirect(url_for("view"))

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("Logged out!")
    return redirect(url_for("login"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
