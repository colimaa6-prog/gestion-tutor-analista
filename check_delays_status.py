
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def check_delays():
    if not DATABASE_URL:
        print("No DATABASE_URL")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        # Get all employees
        cursor.execute("SELECT id, full_name FROM employees")
        employees = cursor.fetchall()
        
        print(f"Checking {len(employees)} employees...")
        
        found_consecutive = 0
        found_accumulated_3 = 0
        
        for emp in employees:
            emp_id = emp[0]
            name = emp[1]
            
            # Check for consecutive
            cursor.execute("""
                SELECT date, status FROM attendance 
                WHERE employee_id = %s 
                ORDER BY date DESC LIMIT 3
            """, (emp_id,))
            last_3 = cursor.fetchall()
            
            is_consecutive = False
            if len(last_3) == 3:
                statuses = [r[1] for r in last_3]
                if all(s == 'delay' for s in statuses):
                    is_consecutive = True
                    found_consecutive += 1
                    print(f"[CONSECUTIVE] {name} has 3 consecutive delays: {[str(r[0]) for r in last_3]}")

            # Check for accumulated in current month (assuming Jan 2026 based on context)
            # Actually just check total in the DB for simplicity or recent timestamps
            # Let's check "Current Month"
            
            # Using current date from system time (2026-01-28)
            cursor.execute("""
                SELECT COUNT(*) FROM attendance 
                WHERE employee_id = %s AND status = 'delay'
                AND EXTRACT(MONTH FROM date) = 1 AND EXTRACT(YEAR FROM date) = 2026
            """, (emp_id,))
            
            count = cursor.fetchone()[0]
            if count >= 3:
                found_accumulated_3 += 1
                prefix = "[ACCUMULATED]" 
                if is_consecutive: prefix += " [ALSO CONSECUTIVE]"
                print(f"{prefix} {name} has {count} delays in Jan 2026")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_delays()
