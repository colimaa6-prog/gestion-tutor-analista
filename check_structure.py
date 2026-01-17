import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== ESTRUCTURA DE USUARIOS ACTUAL ===\n")
    
    # Obtener todos los usuarios
    cur.execute("""
        SELECT id, username, role, supervisor_id 
        FROM users 
        ORDER BY role DESC, username
    """)
    
    users = cur.fetchall()
    
    print(f"{'ID':<5} {'Username':<30} {'Role':<20} {'Supervisor ID':<15}")
    print("-" * 75)
    
    admins = []
    tutors = []
    
    for user_id, username, role, supervisor_id in users:
        print(f"{user_id:<5} {username:<30} {role:<20} {supervisor_id if supervisor_id else 'None':<15}")
        if role == 'admin':
            admins.append((user_id, username))
        elif role == 'tutor_analista':
            tutors.append((user_id, username, supervisor_id))
    
    print(f"\n{'='*75}")
    print(f"Total Admins: {len(admins)}")
    print(f"Total Tutores: {len(tutors)}")
    
    # Mostrar estructura de supervisión
    print("\n=== ESTRUCTURA DE SUPERVISIÓN ===\n")
    for admin_id, admin_name in admins:
        supervised = [t for t in tutors if t[2] == admin_id]
        print(f"\n{admin_name} (ID {admin_id}): supervisa {len(supervised)} tutores")
        for tutor_id, tutor_name, _ in supervised:
            print(f"  - {tutor_name} (ID {tutor_id})")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
