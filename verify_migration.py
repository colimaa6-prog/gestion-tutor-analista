import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

PG_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(PG_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\n=== VERIFICACION DE DATOS EN RAILWAY ===\n")
    
    # 1. Verificar empleados con fechas
    cur.execute("SELECT COUNT(*) FROM employees WHERE hire_date IS NOT NULL")
    count = cur.fetchone()[0]
    print(f"1. Empleados con fecha de ingreso: {count}")
    
    # 2. Mostrar algunos empleados
    cur.execute("SELECT id, full_name, hire_date FROM employees LIMIT 5")
    print("\n2. Primeros 5 empleados:")
    for row in cur.fetchall():
        print(f"   ID {row[0]}: {row[1]} - {row[2]}")
    
    # 3. Verificar roster
    cur.execute("SELECT COUNT(*) FROM attendance_roster")
    roster_count = cur.fetchone()[0]
    print(f"\n3. Colaboradores en roster de asistencias: {roster_count}")
    
    # 4. Verificar usuarios
    cur.execute("SELECT COUNT(*) FROM users")
    users_count = cur.fetchone()[0]
    print(f"\n4. Usuarios totales: {users_count}")
    
    # 5. Verificar branches
    cur.execute("SELECT COUNT(*) FROM branches")
    branches_count = cur.fetchone()[0]
    print(f"\n5. Sucursales totales: {branches_count}")
    
    print("\n=== VERIFICACION COMPLETADA ===\n")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
