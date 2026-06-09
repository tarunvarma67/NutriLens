from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "nutrilens_super_secret_key_2026"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("nutrilens.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id, username, password_hash FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(user[2], password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/dashboard")

        return "Invalid Username or Password"

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

        session["user_id"] = user_id
        session["username"] = username

        return redirect("/onboarding")
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect("nutrilens.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT daily_calories,
           protein_goal,
           fat_goal,
           carb_goal,
           fiber_goal,
           water_goal
    FROM users
    WHERE user_id=?
    """, (session["user_id"],))

    user = cursor.fetchone()

    connection.close()

    current_date = datetime.now().strftime("%A, %B %d")

    return render_template(
        "dashboard.html",
        username=session["username"],
        current_date=current_date,
        daily_calories=user[0],
        protein_goal=user[1],
        fat_goal=user[2],
        carb_goal=user[3],
        fiber_goal=user[4],
        water_goal=user[5]
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/onboarding")
def onboarding():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("onboarding_welcome.html")

@app.route("/profile-form", methods=["GET", "POST"])
def profile_form():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        age = int(request.form["age"])
        gender = request.form["gender"]
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        activity_level = request.form["activity_level"]
        goal = request.form["goal"]

        # BMR
        if gender == "Male":
            bmr = (
                (10 * weight)
                + (6.25 * height)
                - (5 * age)
                + 5
            )
        else:
            bmr = (
                (10 * weight)
                + (6.25 * height)
                - (5 * age)
                - 161
            )

        # TDEE
        if activity_level == "Sedentary":
            tdee = bmr * 1.2

        elif activity_level == "Light":
            tdee = bmr * 1.375

        elif activity_level == "Moderate":
            tdee = bmr * 1.55

        else:
            tdee = bmr * 1.725

        # Goal adjustment
        daily_calories = tdee

        if goal == "Lose Weight":
            daily_calories -= 300

        elif goal == "Gain Weight":
            daily_calories += 300

        daily_calories = round(daily_calories)

        # Macros
        protein_goal = round((daily_calories * 0.25) / 4)
        fat_goal = round((daily_calories * 0.30) / 9)
        carb_goal = round((daily_calories * 0.45) / 4)

        # Fiber
        fiber_goal = round((daily_calories / 1000) * 14)

        # Water
        water_goal = (weight * 35) / 1000

        if activity_level == "Light":
            water_goal += 0.25

        elif activity_level == "Moderate":
            water_goal += 0.50

        elif activity_level == "Very Active":
            water_goal += 0.75

        water_goal = round(water_goal, 1)

        connection = sqlite3.connect("nutrilens.db")
        cursor = connection.cursor()

        cursor.execute("""
        UPDATE users
        SET age=?,
            gender=?,
            height=?,
            weight=?,
            activity_level=?,
            goal=?,
            daily_calories=?,
            protein_goal=?,
            fat_goal=?,
            carb_goal=?,
            fiber_goal=?,
            water_goal=?,
            onboarding_completed=1
        WHERE user_id=?
        """, (
            age,
            gender,
            height,
            weight,
            activity_level,
            goal,
            daily_calories,
            protein_goal,
            fat_goal,
            carb_goal,
            fiber_goal,
            water_goal,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        return redirect("/dashboard")

    return render_template("profile_form.html")
if __name__ == "__main__":
    app.run(debug=True, port=5001)