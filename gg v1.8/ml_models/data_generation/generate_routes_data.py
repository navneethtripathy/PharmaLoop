"""
Generate training data for Model 3: Redistribution Scoring
Creates routes.db with 100 records
"""
import sqlite3
import random
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / 'databases' / 'routes.db'
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS redistribution")

cursor.execute("""
CREATE TABLE redistribution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name TEXT,
    surplus_probability REAL,
    predicted_demand REAL,
    days_to_expiry INTEGER,
    distance_km REAL,
    redistribution_score REAL,
    decision TEXT
)
""")

meds = ["Paracetamol", "Ibuprofen", "Amoxicillin"]

rows = []

for _ in range(100):
    med = random.choice(meds)
    surplus = round(random.uniform(0.5, 1), 2)
    demand = random.randint(50, 500)
    expiry = random.randint(5, 90)
    distance = random.randint(5, 200)
    
    rows.append((med, surplus, demand, expiry, distance))

cursor.executemany("""
INSERT INTO redistribution
(medicine_name, surplus_probability, predicted_demand,
days_to_expiry, distance_km)
VALUES (?, ?, ?, ?, ?)
""", rows)

conn.commit()
conn.close()

print(f"✅ Redistribution data created in {DB_PATH}")
