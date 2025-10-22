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

class users(db.Model):
	id = db.Column("id", db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))

	def __init__(self, name, email):
		self.name = name
		self.email = email

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/view')
def view():
	return render_template('view.html', values=users.query.all())

@app.route('/delete/<int:user_id>')
def delete(user_id):
	user_to_delete = users.query.get(user_id)
	if user_to_delete:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User deleted Successfully", "success")
	else:
		flash("User not found", "error")
	return redirect(url_for('view'))

@app.route('/login', methods=["POST", "GET"])
def login():
	if request.method == "POST":
		session.permanent = True
		user = request.form["nm"]
		session["user"] = user

		found_user = users.query.filter_by(name=user).first()
		if found_user:
			session["email"] = found_user.email
		else:
			usr = users(user, "")
			db.session.add(usr)
			db.session.commit()

		flash("Login Successful!")
		return redirect(url_for("user"))
	else:
		if "user" in session:
			flash("Already logged in!")
			return redirect(url_for("user"))
		return render_template("login.html")
				
@app.route('/user', methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Your email as been saved!")
        else:
        	if "email" in session:
        		email = session["email"]
        return render_template("user.html", email=email)
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
		app.run(debug=True)
	

