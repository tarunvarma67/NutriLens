import sqlite3

connection = sqlite3.connect("nutrilens.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id TEXT UNIQUE,

    full_name TEXT,

    username TEXT UNIQUE,

    email TEXT UNIQUE,

    password_hash TEXT,

    age INTEGER,

    gender TEXT,

    height REAL,

    weight REAL,

    goal TEXT,

    activity_level TEXT,

    daily_calories INTEGER,

    protein_goal INTEGER,

    water_goal REAL,

    onboarding_completed INTEGER DEFAULT 0

)
""")

connection.commit()

connection.close()

print("Database Created Successfully")