import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== DIAGNÓSTICO COMPLETO ===\n")
    
    # 1. Verificar roster
    print("1. ROSTER DE ASISTENCIAS:")
    cur.execute("""
        SELECT ar.id, ar.employee_id, ar.added_by_user_id, 
               e.full_name, u.username as added_by
        FROM attendance_roster ar
        JOIN employees e ON ar.employee_id = e.id
        JOIN users u ON ar.added_by_user_id = u.id
        ORDER BY ar.id
    """)
    
    roster = cur.fetchall()
    if roster:
        for row in roster:
            print(f"  ID {row[0]}: {row[3]} (employee_id={row[1]}) - Agregado por: {row[4]} (user_id={row[2]})")
    else:
        print("  (vacío)")
    
    # 2. Verificar qué devuelve get_authorized_user_ids para user_id=1
    print("\n2. IDS AUTORIZADOS PARA USER_ID=1:")
    cur.execute("SELECT id, role, supervisor_id FROM users WHERE id = 1")
    user = cur.fetchone()
    if user:
        print(f"  Usuario: ID={user[0]}, Role={user[1]}, Supervisor={user[2]}")
        
        if user[1] == 'admin':
            cur.execute("SELECT id FROM users WHERE supervisor_id = %s", (user[0],))
            supervised = cur.fetchall()
            supervised_ids = [row[0] for row in supervised]
            supervised_ids.append(user[0])
            print(f"  IDs autorizados: {supervised_ids}")
        else:
            print(f"  IDs autorizados: [{user[0]}]")
    
    # 3. Verificar empleados
    print("\n3. EMPLEADOS EN LA BASE:")
    cur.execute("SELECT COUNT(*) FROM employees")
    count = cur.fetchone()[0]
    print(f"  Total: {count}")
    
    # 4. Verificar incidentes
    print("\n4. INCIDENTES:")
    cur.execute("SELECT COUNT(*) FROM incidents")
    count = cur.fetchone()[0]
    print(f"  Total: {count}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
