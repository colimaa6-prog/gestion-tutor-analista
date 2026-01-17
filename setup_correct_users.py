import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

# Estructura correcta de usuarios
CORRECT_USERS = {
    'admins': [
        {'username': 'HELDER MORA', 'password': 'admin123', 'id': 1},
        {'username': 'ESTHFANIA RAMOS', 'password': 'admin123', 'id': 2}
    ],
    'tutors_admin1': [  # Supervisados por HELDER MORA (ID 1)
        {'username': 'KAREM JANETH', 'password': 'Exitus.tap'},
        {'username': 'ANA CARLOTA', 'password': 'Exitus.gua'},
        {'username': 'CHRISTINE', 'password': 'Exitus.san'},
        {'username': 'JESSICA', 'password': 'Exitus.car'},
        {'username': 'MARIA ANTONIA', 'password': 'Exitus.tam'},
        {'username': 'KARLA MARINA', 'password': 'Exitus.apo'}
    ],
    'tutors_admin2': [  # Supervisados por ESTHFANIA RAMOS (ID 2)
        {'username': 'ARANZAZU', 'password': 'Exitus.tec'},
        {'username': 'DULCE MARLEN', 'password': 'Exitus.zih'},
        {'username': 'SANDRA RUTH', 'password': 'Exitus.ayo'},
        {'username': 'ROSALIA', 'password': 'Exitus.chi'},
        {'username': 'MARIA ISABEL', 'password': 'Exitus.ixt'},
        {'username': 'MARIELA SOLEDAD', 'password': 'Exitus.ver'}
    ]
}

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== LIMPIEZA Y CONFIGURACIÓN DE USUARIOS ===\n")
    
    # 1. Eliminar todos los usuarios excepto los admins
    print("1. Eliminando usuarios incorrectos...")
    cur.execute("DELETE FROM users WHERE role = 'tutor_analista'")
    print(f"   ✓ Tutores eliminados")
    
    # 2. Actualizar admins
    print("\n2. Actualizando administradores...")
    for admin in CORRECT_USERS['admins']:
        cur.execute("""
            UPDATE users 
            SET username = %s, password_hash = %s, supervisor_id = NULL
            WHERE id = %s
        """, (admin['username'], admin['password'], admin['id']))
        print(f"   ✓ {admin['username']} (ID {admin['id']})")
    
    # 3. Crear tutores para admin 1
    print(f"\n3. Creando tutores para HELDER MORA (ID 1)...")
    for tutor in CORRECT_USERS['tutors_admin1']:
        cur.execute("""
            INSERT INTO users (username, password_hash, role, supervisor_id)
            VALUES (%s, %s, 'tutor_analista', 1)
        """, (tutor['username'], tutor['password']))
        print(f"   ✓ {tutor['username']}")
    
    # 4. Crear tutores para admin 2
    print(f"\n4. Creando tutores para ESTHFANIA RAMOS (ID 2)...")
    for tutor in CORRECT_USERS['tutors_admin2']:
        cur.execute("""
            INSERT INTO users (username, password_hash, role, supervisor_id)
            VALUES (%s, %s, 'tutor_analista', 2)
        """, (tutor['username'], tutor['password']))
        print(f"   ✓ {tutor['username']}")
    
    # 5. Verificar resultado
    print("\n=== VERIFICACIÓN FINAL ===\n")
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'tutor_analista' AND supervisor_id = 1")
    tutors_admin1 = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'tutor_analista' AND supervisor_id = 2")
    tutors_admin2 = cur.fetchone()[0]
    
    print(f"Administradores: {admin_count}")
    print(f"Tutores de HELDER MORA: {tutors_admin1}")
    print(f"Tutores de ESTHFANIA RAMOS: {tutors_admin2}")
    print(f"Total usuarios: {admin_count + tutors_admin1 + tutors_admin2}")
    
    if admin_count == 2 and tutors_admin1 == 6 and tutors_admin2 == 6:
        print("\n✅ ESTRUCTURA CORRECTA: 2 admins + 12 tutores (6 por admin)\n")
    else:
        print("\n⚠️ ADVERTENCIA: La estructura no es la esperada\n")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
