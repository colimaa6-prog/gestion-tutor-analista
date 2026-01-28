
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def backfill_alerts():
    if not DATABASE_URL:
        print("No DATABASE_URL")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        # Get employees
        cursor.execute("SELECT id, full_name FROM employees")
        employees = cursor.fetchall()

        print(f"Checking {len(employees)} employees for accumulated delays backfill...")
        
        count_alerts = 0
        
        # Hardcoded for Jan 2026 based on user context, or use current date
        # Check current month
        today = datetime.now()
        # Assume user is working on Jan 2026 data
        target_month = 1
        target_year = 2026 
        
        for emp in employees:
            emp_id = emp[0]
            emp_name = emp[1]
            
            # Count delays
            cursor.execute("""
                SELECT date, comment 
                FROM attendance 
                WHERE employee_id = %s 
                AND status = 'delay'
                AND EXTRACT(MONTH FROM date) = %s
                AND EXTRACT(YEAR FROM date) = %s
                ORDER BY date ASC
            """, (emp_id, target_month, target_year))
            
            records = cursor.fetchall()
            count = len(records)
            
            if count >= 3:
                # Check roster
                cursor.execute("""
                    SELECT ar.added_by_user_id, u.supervisor_id
                    FROM attendance_roster ar
                    JOIN users u ON ar.added_by_user_id = u.id
                    WHERE ar.employee_id = %s
                """, (emp_id,))
                
                roster = cursor.fetchone()
                if not roster:
                    print(f"Skipping {emp_name}: No roster info")
                    continue
                    
                tutor_id = roster[0]
                supervisor_id = roster[1]
                
                # Create Alert Payload
                month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                month_name = month_names[target_month]
                latest_date_str = records[-1][0].isoformat() if hasattr(records[-1][0], 'isoformat') else str(records[-1][0])
                
                alert_details = json.dumps({
                    'type': '3_delays',
                    'subtype': 'accumulated',
                    'employee_name': emp_name,
                    'month': month_name,
                    'year': target_year,
                    'count': count,
                    'latest_date': latest_date_str,
                    'delays': [
                        {
                            'date': r[0].isoformat() if hasattr(r[0], 'isoformat') else str(r[0]), 
                            'comment': r[1]
                        } 
                        for r in records
                    ]
                })
                
                # Insert Alert if not exists
                def insert_alert(uid):
                    searchTerm = f'"month": "{month_name}", "year": {target_year}'
                    cursor.execute("""
                        SELECT id FROM alerts 
                        WHERE user_id = %s AND employee_id = %s AND details LIKE %s
                    """, (uid, emp_id, f'%{searchTerm}%'))
                    
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO alerts (user_id, employee_id, details)
                            VALUES (%s, %s, %s)
                        """, (uid, emp_id, alert_details))
                        return True
                    return False

                if insert_alert(tutor_id): count_alerts += 1
                if supervisor_id:
                     if insert_alert(supervisor_id): count_alerts += 1
                     
        conn.commit()
        print(f"Backfill complete. Created {count_alerts} alerts.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    backfill_alerts()
