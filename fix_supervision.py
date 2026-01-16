import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== CORRIGIENDO ESTRUCTURA DE SUPERVISIÓN ===\n")
    
    # 1. Obtener administradores
    cur.execute("SELECT id, username FROM users WHERE role = 'admin' ORDER BY id")
    admins = cur.fetchall()
    
    if len(admins) != 2:
        print(f"ERROR: Se esperaban 2 admins, se encontraron {len(admins)}")
        exit(1)
    
    admin1_id, admin1_name = admins[0]
    admin2_id, admin2_name = admins[1]
    
    print(f"Admin 1: ID {admin1_id} - {admin1_name}")
    print(f"Admin 2: ID {admin2_id} - {admin2_name}")
    
    # 2. Obtener tutores
    cur.execute("SELECT id, username FROM users WHERE role = 'tutor_analista' ORDER BY id")
    tutors = cur.fetchall()
    
    total_tutors = len(tutors)
    print(f"\nTotal tutores encontrados: {total_tutors}")
    
    # 3. Dividir tutores equitativamente
    mid_point = total_tutors // 2
    tutors_admin1 = tutors[:mid_point]
    tutors_admin2 = tutors[mid_point:]
    
    print(f"\n--- Asignando {len(tutors_admin1)} tutores a {admin1_name} ---")
    for tutor_id, tutor_name in tutors_admin1:
        cur.execute("UPDATE users SET supervisor_id = %s WHERE id = %s", (admin1_id, tutor_id))
        print(f"  ✓ {tutor_name} (ID {tutor_id})")
    
    print(f"\n--- Asignando {len(tutors_admin2)} tutores a {admin2_name} ---")
    for tutor_id, tutor_name in tutors_admin2:
        cur.execute("UPDATE users SET supervisor_id = %s WHERE id = %s", (admin2_id, tutor_id))
        print(f"  ✓ {tutor_name} (ID {tutor_id})")
    
    # 4. Verificar resultado
    print("\n=== VERIFICACIÓN FINAL ===\n")
    
    cur.execute("""
        SELECT COUNT(*) 
        FROM users 
        WHERE role = 'tutor_analista' AND supervisor_id = %s
    """, (admin1_id,))
    count1 = cur.fetchone()[0]
    
    cur.execute("""
        SELECT COUNT(*) 
        FROM users 
        WHERE role = 'tutor_analista' AND supervisor_id = %s
    """, (admin2_id,))
    count2 = cur.fetchone()[0]
    
    print(f"{admin1_name}: {count1} tutores supervisados")
    print(f"{admin2_name}: {count2} tutores supervisados")
    
    print("\n✅ ESTRUCTURA DE SUPERVISIÓN CORREGIDA\n")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
