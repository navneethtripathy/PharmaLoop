"""
Generate training data for Model 2: Demand Forecasting
Creates demand.db with 500 records
"""
import sqlite3
import random
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / 'databases' / 'demand.db'
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS clinic_demand")

cursor.execute("""
CREATE TABLE clinic_demand (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name TEXT,
    past_month_usage INTEGER,
    clinic_population INTEGER,
    disease_index REAL,
    season INTEGER,
    next_month_demand INTEGER,
    predicted_demand REAL
)
""")

medicines = [
    "Paracetamol", "Amoxicillin", "Ibuprofen", "Ciprofloxacin",
    "Metformin", "Aspirin", "Azithromycin", "Doxycycline"
]

rows = []

for i in range(500):
    name = random.choice(medicines)
    past = random.randint(20, 400)
    pop = random.randint(500, 10000)
    disease = round(random.uniform(0, 1), 2)
    season = random.randint(0, 1)
    
    # Realistic demand formula (label)
    demand = int(
        past * 0.6 +
        pop * 0.02 +
        disease * 200 +
        season * 50 +
        random.randint(-20, 20)
    )
    
    rows.append((name, past, pop, disease, season, demand))

cursor.executemany("""
INSERT INTO clinic_demand
(medicine_name, past_month_usage, clinic_population,
disease_index, season, next_month_demand)
VALUES (?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()
conn.close()

print(f"✅ 500 demand records created in {DB_PATH}")
