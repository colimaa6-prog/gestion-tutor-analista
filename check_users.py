import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== ESTRUCTURA DE USUARIOS ===\n")
    
    # Verificar usuarios
    cur.execute("""
        SELECT id, username, role, supervisor_id 
        FROM users 
        ORDER BY role DESC, id
    """)
    
    print("Usuarios en la base de datos:")
    print("-" * 80)
    admins = []
    tutors = []
    
    for row in cur.fetchall():
        user_id, username, role, supervisor_id = row
        print(f"ID {user_id:3d}: {username:40s} | Role: {role:15s} | Supervisor: {supervisor_id}")
        if role == 'admin':
            admins.append(user_id)
        elif role == 'tutor_analista':
            tutors.append((user_id, supervisor_id))
    
    print(f"\nTotal Admins: {len(admins)}")
    print(f"Total Tutores: {len(tutors)}")
    
    # Verificar supervisión
    print("\n=== ESTRUCTURA DE SUPERVISIÓN ===\n")
    for admin_id in admins:
        cur.execute("SELECT username FROM users WHERE id = %s", (admin_id,))
        admin_name = cur.fetchone()[0]
        
        supervised = [t[0] for t in tutors if t[1] == admin_id]
        print(f"Admin {admin_id} ({admin_name}): supervisa {len(supervised)} tutores")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
