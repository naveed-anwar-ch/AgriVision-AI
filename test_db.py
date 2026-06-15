import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# Check tables exist
print("📌 Tables in database:")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(c.fetchall())

# Check USERS data
print("\n👤 USERS DATA:")
c.execute("SELECT * FROM users")
print(c.fetchall())

# Check PREDICTIONS data
print("\n🌿 PREDICTIONS DATA:")
c.execute("SELECT * FROM predictions")
print(c.fetchall())

conn.close()