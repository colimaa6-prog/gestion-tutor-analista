import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== LISTADO COMPLETO DE USUARIOS ===\n")
    
    cur.execute("""
        SELECT id, username, role, supervisor_id 
        FROM users 
        ORDER BY role DESC, id
    """)
    
    print(f"{'ID':<5} {'Username':<40} {'Role':<20} {'Supervisor ID':<15}")
    print("-" * 85)
    
    admins = []
    tutors = []
    others = []
    
    for row in cur.fetchall():
        user_id, username, role, supervisor_id = row
        print(f"{user_id:<5} {username:<40} {role:<20} {supervisor_id if supervisor_id else 'None':<15}")
        
        if role == 'admin':
            admins.append((user_id, username))
        elif role == 'tutor_analista':
            tutors.append((user_id, username, supervisor_id))
        else:
            others.append((user_id, username, role))
    
    print(f"\n{'='*85}")
    print(f"Total Administradores: {len(admins)}")
    print(f"Total Tutores Analistas: {len(tutors)}")
    print(f"Otros roles: {len(others)}")
    
    if others:
        print("\nOtros roles encontrados:")
        for user_id, username, role in others:
            print(f"  - {username} ({role})")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
