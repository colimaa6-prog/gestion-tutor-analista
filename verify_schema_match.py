
import sqlite3
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

try:
    conn = sqlite3.connect('gestion_tutor.db')
    cursor = conn.cursor()
    
    tables_to_check = {
        'branches': ['id', 'name', 'location'],
        'users': ['id', 'username', 'password_hash', 'role', 'supervisor_id', 'branch_id'],
        'employees': ['id', 'full_name', 'branch_id', 'hire_date', 'status'],
        'attendance_roster': ['id', 'employee_id', 'added_by_user_id'],
        'incidents': ['id', 'branch_id', 'reported_by', 'type', 'status', 'description', 'start_date', 'end_date', 'created_at'],
        'attendance': ['id', 'employee_id', 'date', 'status', 'comment', 'arrival_time', 'permission_type', 'start_date', 'end_date'],
        'reports': ['id', 'employee_id', 'month', 'year', 'data']
    }

    print("--- Verifying Columns ---")
    for table_name, requested_cols in tables_to_check.items():
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        missing = [col for col in requested_cols if col not in existing_cols]
        if missing:
            print(f"⚠️  Table '{table_name}' MISSING columns: {missing}")
        else:
            print(f"✅ Table '{table_name}' has all required columns.")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
