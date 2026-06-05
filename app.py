from flask import Flask, render_template, request
import sqlite3
import re

from werkzeug.security import generate_password_hash

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        full_name = request.form["full_name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match"

        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

        if not re.match(password_pattern, password):
            return "Password must contain uppercase, lowercase, number and special character"

        connection = sqlite3.connect("nutrilens.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            connection.close()
            return "Username already taken"

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_email = cursor.fetchone()

        if existing_email:
            connection.close()
            return "Email already registered"

        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

        user_id = f"NL{count + 1:04d}"

        hashed_password = generate_password_hash(password)

        cursor.execute("""
        INSERT INTO users
        (user_id, full_name, username, email, password_hash)
        VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            full_name,
            username,
            email,
            hashed_password
        ))

        connection.commit()
        connection.close()

        return f"Account Created Successfully! Your User ID is {user_id}"

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)