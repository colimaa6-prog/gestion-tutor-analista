import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== ACTUALIZANDO CONTRASEÑAS DE ADMINISTRADORES ===\n")
    
    # Actualizar contraseña de HELDER MORA
    cur.execute("""
        UPDATE users 
        SET password_hash = 'Hmora'
        WHERE username = 'HELDER MORA' AND role = 'admin'
    """)
    print("✓ Contraseña de HELDER MORA actualizada a: Hmora")
    
    # Actualizar contraseña de ESTHEFANIA RAMOS
    cur.execute("""
        UPDATE users 
        SET password_hash = 'Eramos'
        WHERE username = 'ESTHFANIA RAMOS' AND role = 'admin'
    """)
    print("✓ Contraseña de ESTHFANIA RAMOS actualizada a: Eramos")
    
    # Verificar
    print("\n=== VERIFICACIÓN ===\n")
    cur.execute("""
        SELECT id, username, password_hash 
        FROM users 
        WHERE role = 'admin'
        ORDER BY id
    """)
    
    for row in cur.fetchall():
        print(f"ID {row[0]}: {row[1]} - Contraseña: {row[2]}")
    
    print("\n✅ CONTRASEÑAS ACTUALIZADAS CORRECTAMENTE\n")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
