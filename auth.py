import sqlite3
import hashlib

# =========================
# DATABASE SETUP
# =========================
DB_NAME = "database.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()


# =========================
# PASSWORD HASHING
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# CREATE USERS TABLE
# =========================
def create_users_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        status TEXT DEFAULT 'active'
    )
    """)
    conn.commit()


# =========================
# CHECK IF USER EXISTS
# =========================
def user_exists(username, email):
    c.execute("""
    SELECT * FROM users WHERE username=? OR email=?
    """, (username, email))

    return c.fetchone() is not None


# =========================
# SIGNUP FUNCTION
# =========================
def signup_user(username, email, password):

    # check duplicates first
    if user_exists(username, email):
        return False

    try:
        c.execute("""
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
        """, (username, email, hash_password(password)))

        conn.commit()
        return True

    except Exception as e:
        print("Signup Error:", e)
        return False


# =========================
# LOGIN FUNCTION
# =========================
def login_user(email, password):

    hashed_password = hash_password(password)

    c.execute("""
    SELECT * FROM users WHERE email=? AND password=?
    """, (email, hashed_password))

    user = c.fetchone()

    return user is not None