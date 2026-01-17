import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== VERIFICACIÓN DE CREDENCIALES ===\n")
    
    # Buscar el usuario KAREM JANETH
    cur.execute("""
        SELECT id, username, password_hash, role, supervisor_id
        FROM users
        WHERE username LIKE '%KAREM%'
    """)
    
    user = cur.fetchone()
    
    if user:
        print(f"Usuario encontrado:")
        print(f"  ID: {user[0]}")
        print(f"  Username: {user[1]}")
        print(f"  Password Hash: {user[2]}")
        print(f"  Role: {user[3]}")
        print(f"  Supervisor ID: {user[4]}")
    else:
        print("Usuario KAREM JANETH no encontrado")
        
        # Listar todos los tutores
        print("\nTodos los tutores:")
        cur.execute("SELECT id, username FROM users WHERE role = 'tutor_analista' ORDER BY id")
        for row in cur.fetchall():
            print(f"  ID {row[0]}: {row[1]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
