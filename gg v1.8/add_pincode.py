import sqlite3

# 🔥 CHANGE THIS to your DB filename
conn = sqlite3.connect("pharmaloop.db")

cursor = conn.cursor()

cursor.execute("ALTER TABLE users ADD COLUMN pincode TEXT;")

conn.commit()
conn.close()

print("✅ pincode column added successfully")
