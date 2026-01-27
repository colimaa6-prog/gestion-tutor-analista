
import sqlite3

db_path = 'gestion_tutor.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = ['users', 'branches', 'employees', 'incidents', 'attendance_roster', 'attendance', 'reports']

print("--- SQLite Table Columns ---")
for table in tables:
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"{table}: {columns}")
    except Exception as e:
        print(f"Error reading {table}: {e}")

conn.close()
