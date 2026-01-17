import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== CREDENCIALES DE ADMINISTRADORES ===\n")
    
    # Obtener admins
    cur.execute("""
        SELECT id, username, password_hash, role
        FROM users
        WHERE role = 'admin'
        ORDER BY id
    """)
    
    for row in cur.fetchall():
        user_id, username, password, role = row
        print(f"ID: {user_id}")
        print(f"Username: '{username}'")
        print(f"Password: '{password}'")
        print(f"Role: {role}")
        print("-" * 50)
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
