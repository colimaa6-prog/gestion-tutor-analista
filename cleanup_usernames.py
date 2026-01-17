import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== LIMPIEZA DE ESPACIOS EN USERNAMES ===\n")
    
    # Actualizar todos los usernames para eliminar espacios extra
    cur.execute("""
        UPDATE users 
        SET username = TRIM(username)
    """)
    
    print("✓ Espacios eliminados de todos los usernames")
    
    # Verificar resultado
    print("\n=== USUARIOS ACTUALIZADOS ===\n")
    cur.execute("SELECT id, username, role FROM users ORDER BY role DESC, id")
    
    for row in cur.fetchall():
        print(f"ID {row[0]}: '{row[1]}' ({row[2]})")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
