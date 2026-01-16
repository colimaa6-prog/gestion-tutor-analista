import sqlite3
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SQLITE_DB = 'gestion_tutor.db'
PG_URL = os.getenv('DATABASE_URL')

print("="*60)
print("🛠️  MIGRACIÓN DE DATOS LOCAL -> RAILWAY (POSTGRESQL)")
print("="*60)

if not PG_URL:
    print("⚠️  No se encontró DATABASE_URL en el archivo .env")
    PG_URL = input("👉 Por favor, pega tu DATABASE_URL de Railway aquí: ").strip()
    if not PG_URL:
        print("❌ URL requerida. Saliendo.")
        exit(1)
else:
    print(f"✅ URL de Postgres detectada en .env")

if not os.path.exists(SQLITE_DB):
    print(f"❌ Base de datos SQLite {SQLITE_DB} no encontrada.")
    exit(1)

print("\n🔗 Conectando a las bases de datos...")

# Connect to SQLite
conn_sqlite = sqlite3.connect(SQLITE_DB)
conn_sqlite.row_factory = sqlite3.Row
cur_sqlite = conn_sqlite.cursor()

# Connect to Postgres
try:
    conn_pg = psycopg2.connect(PG_URL)
    cur_pg = conn_pg.cursor()
    print("✅ Conectado a PostgreSQL")
except Exception as e:
    print(f"❌ Error al conectar a Postgres: {e}")
    exit(1)

# 1. Ensure Schema
print("\n🏗️  Verificando estructura de la base de datos...")
if os.path.exists('init_postgres.sql'):
    with open('init_postgres.sql', 'r', encoding='utf-8') as f:
        sql_schema = f.read()
    try:
        cur_pg.execute(sql_schema)
        conn_pg.commit()
        print("✅ Esquema y datos base (init_postgres.sql) aplicados correctamente.")
    except Exception as e:
        conn_pg.rollback()
        print(f"⚠️  Advertencia al aplicar esquema: {e}")
else:
    print("⚠️  init_postgres.sql no encontrado. Asumiendo que las tablas ya existen.")

# 2. Migration Function
def migrate_table(table, cols, conflict_target='id'):
    print(f"\n📦 Migrando tabla: {table}")
    
    # Read from SQLite
    try:
        cur_sqlite.execute(f"SELECT {', '.join(cols)} FROM {table}")
        rows = cur_sqlite.fetchall()
    except Exception as e:
        print(f"  ❌ Error leyendo {table} de SQLite: {e}")
        return

    total_rows = len(rows)
    print(f"  Encontrados {total_rows} registros en SQLite.")
    
    if total_rows == 0:
        return

    # Prepare SQL Insert
    cols_sql = sql.SQL(', ').join(map(sql.Identifier, cols))
    placeholders = sql.SQL(', ').join(sql.Placeholder() * len(cols))
    
    # Use explicit columns to support inserting IDs
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO NOTHING").format(
        sql.Identifier(table),
        cols_sql,
        placeholders,
        sql.Identifier(conflict_target)
    )

    success = 0
    errors = 0
    deferred_rows = []
    
    # Insert row by row to handle FK constraints gracefully
    for row in rows:
        row_data = tuple(row)
        try:
            cur_pg.execute(insert_query, row_data)
            if cur_pg.rowcount > 0:
                success += 1
        except psycopg2.errors.ForeignKeyViolation:
            conn_pg.rollback()
            deferred_rows.append(row_data)
        except Exception as e:
            conn_pg.rollback()
            print(f"  ❌ Error en fila ID={row['id']}: {e}")
            errors += 1
        else:
            conn_pg.commit()
            
    # Retry deferred rows
    if deferred_rows:
        print(f"  🔄 Reintentando {len(deferred_rows)} filas pospuestas (dependencias FK)...")
        for row_data in deferred_rows:
            try:
                cur_pg.execute(insert_query, row_data)
                if cur_pg.rowcount > 0:
                    success += 1
                conn_pg.commit()
            except Exception as e:
                conn_pg.rollback()
                print(f"  ❌ Falló reintento: {e}")
                errors += 1
                
    print(f"  ✅ Completado: {success} insertados, {total_rows - success - errors} omitidos (ya existían), {errors} errores.")

    # Reset Sequence to max(id) + 1
    if 'id' in cols and success > 0:
        try:
            cur_pg.execute(sql.SQL("SELECT setval(pg_get_serial_sequence({}, 'id'), COALESCE(MAX(id), 0) + 1, false) FROM {}").format(sql.Identifier(table), sql.Identifier(table)))
            conn_pg.commit()
            # print("  🔢 Secuencia reiniciada.")
        except Exception as e:
            conn_pg.rollback()

# Tables ordered by dependency
tables = [
    ('branches', ['id', 'name', 'location']),
    ('users', ['id', 'username', 'password_hash', 'role', 'supervisor_id', 'branch_id']),
    ('employees', ['id', 'full_name', 'branch_id', 'hire_date', 'status']),
    ('attendance_roster', ['id', 'employee_id', 'added_by_user_id']),
    ('incidents', ['id', 'branch_id', 'reported_by', 'type', 'status', 'description', 'start_date', 'end_date', 'created_at']),
    ('attendance', ['id', 'employee_id', 'date', 'status', 'comment', 'arrival_time', 'permission_type', 'start_date', 'end_date']),
    ('reports', ['id', 'employee_id', 'month', 'year', 'data'])
]

print("\n🚀 Iniciando Migración de Datos...")

for t_name, t_cols in tables:
    migrate_table(t_name, t_cols)

print("\n✨ Migración finalizada exitosamente.")
print("Tu base de datos en Railway ahora tiene los datos locales.")
cur_pg.close()
conn_pg.close()
conn_sqlite.close()
