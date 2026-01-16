import sqlite3
import psycopg2
from psycopg2 import sql
import os
import sys
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB = 'gestion_tutor.db'
PG_URL = os.getenv('DATABASE_URL')

print("=" * 60)
print("MIGRACION DE DATOS LOCAL -> RAILWAY")
print("=" * 60)

if not PG_URL:
    print("No se encontro DATABASE_URL en .env")
    exit(1)

print("OK: URL encontrada")

if not os.path.exists(SQLITE_DB):
    print(f"ERROR: {SQLITE_DB} no encontrado")
    exit(1)

print("Conectando...")

conn_sqlite = sqlite3.connect(SQLITE_DB)
conn_sqlite.row_factory = sqlite3.Row
cur_sqlite = conn_sqlite.cursor()

try:
    conn_pg = psycopg2.connect(PG_URL)
    conn_pg.set_session(autocommit=True)
    cur_pg = conn_pg.cursor()
    print("OK: Conectado a PostgreSQL\n")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

def migrate_table(table, cols):
    print(f"Migrando {table}...", end=" ")
    
    try:
        cur_sqlite.execute(f"SELECT {', '.join(cols)} FROM {table}")
        rows = cur_sqlite.fetchall()
    except Exception as e:
        print(f"ERROR: {e}")
        return

    if len(rows) == 0:
        print("(vacia)")
        return

    cols_sql = sql.SQL(', ').join(map(sql.Identifier, cols))
    placeholders = sql.SQL(', ').join(sql.Placeholder() * len(cols))
    
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (id) DO NOTHING").format(
        sql.Identifier(table),
        cols_sql,
        placeholders
    )

    success = 0
    deferred = []
    
    for row in rows:
        try:
            cur_pg.execute(insert_query, tuple(row))
            success += 1
        except psycopg2.errors.ForeignKeyViolation:
            deferred.append(tuple(row))
        except Exception:
            pass
            
    # Retry deferred
    for row_data in deferred:
        try:
            cur_pg.execute(insert_query, row_data)
            success += 1
        except Exception:
            pass
                
    print(f"{success}/{len(rows)} registros")

    # Reset sequence
    if 'id' in cols:
        try:
            cur_pg.execute(sql.SQL("SELECT setval(pg_get_serial_sequence({}, 'id'), COALESCE(MAX(id), 0) + 1, false) FROM {}").format(
                sql.Identifier(table), sql.Identifier(table)))
        except Exception:
            pass

tables = [
    ('branches', ['id', 'name', 'location']),
    ('users', ['id', 'username', 'password_hash', 'role', 'supervisor_id', 'branch_id']),
    ('employees', ['id', 'full_name', 'branch_id', 'hire_date', 'status']),
    ('attendance_roster', ['id', 'employee_id', 'added_by_user_id']),
    ('incidents', ['id', 'branch_id', 'reported_by', 'type', 'status', 'description', 'start_date', 'end_date', 'created_at']),
    ('attendance', ['id', 'employee_id', 'date', 'status', 'comment', 'arrival_time', 'permission_type', 'start_date', 'end_date']),
    ('reports', ['id', 'employee_id', 'month', 'year', 'data'])
]

for t_name, t_cols in tables:
    migrate_table(t_name, t_cols)

print("\n" + "=" * 60)
print("MIGRACION COMPLETADA")
print("=" * 60)

cur_pg.close()
conn_pg.close()
conn_sqlite.close()
