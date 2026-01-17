import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== DIAGNÓSTICO DE ROSTER Y REPORTES ===\n")
    
    # 1. Verificar usuario KAREM JANETH
    cur.execute("""
        SELECT id, username, role, supervisor_id
        FROM users
        WHERE username LIKE '%KAREM%'
    """)
    user = cur.fetchone()
    if user:
        user_id, username, role, supervisor_id = user
        print(f"Usuario: {username} (ID {user_id})")
        print(f"Role: {role}")
        print(f"Supervisor ID: {supervisor_id}")
    else:
        print("Usuario KAREM JANETH no encontrado")
        exit(1)
    
    # 2. Verificar IDs autorizados para este usuario
    print(f"\n--- IDs Autorizados para user_id={user_id} ---")
    if role == 'admin':
        cur.execute("SELECT id FROM users WHERE supervisor_id = %s", (user_id,))
        supervised = cur.fetchall()
        authorized_ids = [row[0] for row in supervised]
        authorized_ids.append(user_id)
        print(f"Admin ve IDs: {authorized_ids}")
    else:
        authorized_ids = [user_id]
        print(f"Tutor ve solo su ID: {authorized_ids}")
    
    # 3. Verificar roster completo
    print("\n--- ROSTER COMPLETO ---")
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
            roster_id, emp_id, added_by_id, emp_name, added_by_name = row
            in_authorized = "✓" if added_by_id in authorized_ids else "✗"
            print(f"{in_authorized} Roster ID {roster_id}: {emp_name} (emp_id={emp_id}) - Agregado por: {added_by_name} (user_id={added_by_id})")
    else:
        print("(roster vacío)")
    
    # 4. Simular query de reportes
    print(f"\n--- QUERY DE REPORTES (userId={user_id}) ---")
    placeholders = ','.join(['%s' for _ in authorized_ids])
    query = f"""
        SELECT DISTINCT e.id, e.full_name, e.branch_id, b.name as branch_name
        FROM attendance_roster ar
        JOIN employees e ON ar.employee_id = e.id
        LEFT JOIN branches b ON e.branch_id = b.id
        WHERE ar.added_by_user_id IN ({placeholders})
        ORDER BY e.full_name ASC
    """
    cur.execute(query, authorized_ids)
    
    results = cur.fetchall()
    if results:
        print(f"Colaboradores que vería en reportes: {len(results)}")
        for row in results:
            print(f"  - {row[1]} (ID {row[0]})")
    else:
        print("NO HAY COLABORADORES (por eso aparece el mensaje)")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
