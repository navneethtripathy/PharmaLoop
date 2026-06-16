"""
Generate training data for Model 1: Surplus Prediction
Creates medicine.db with 500 records
"""
import sqlite3
import random
from pathlib import Path

# Save database in project root or databases folder
DB_PATH = Path(__file__).resolve().parent.parent.parent / 'databases' / 'medicine.db'
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS medicine_batches")

cursor.execute("""
CREATE TABLE medicine_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name TEXT,
    current_stock INTEGER,
    avg_monthly_usage INTEGER,
    days_to_expiry INTEGER,
    hospital_type INTEGER,
    surplus INTEGER,
    surplus_probability REAL,
    status TEXT
)
""")

medicine_names = [
    "Paracetamol", "Amoxicillin", "Ibuprofen", "Ciprofloxacin",
    "Metformin", "Aspirin", "Azithromycin", "Doxycycline",
    "Omeprazole", "Cetirizine"
]

rows = []

for i in range(500):
    name = random.choice(medicine_names) + "_" + str(i)
    stock = random.randint(50, 2000)
    usage = random.randint(10, 800)
    expiry = random.randint(5, 180)
    hospital = random.randint(0, 1)
    
    # Label logic (training)
    surplus = 1 if (stock > usage and expiry < 60) else 0
    
    rows.append((name, stock, usage, expiry, hospital, surplus))

cursor.executemany("""
INSERT INTO medicine_batches
(medicine_name, current_stock, avg_monthly_usage,
days_to_expiry, hospital_type, surplus)
VALUES (?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()
conn.close()

print(f"✅ 500 medicines inserted in {DB_PATH}")
