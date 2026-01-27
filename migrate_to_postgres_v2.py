
import sqlite3
import psycopg2
from psycopg2 import sql
import os
import sys
from dotenv import load_dotenv

# Force UTF-8 for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

SQLITE_DB = 'gestion_tutor.db'
PG_URL = os.getenv('DATABASE_URL')

print("="*60)
print("🛠️  MIGRACIÓN DE DATOS LOCAL -> NEON / RENDER")
print("="*60)

if not PG_URL:
    print("⚠️  No se encontró DATABASE_URL en el archivo .env")
    PG_URL = input("👉 Por favor, pega tu DATABASE_URL de Neon aquí: ").strip()
    if not PG_URL:
        print("❌ URL requerida. Saliendo.")
        sys.exit(1)
else:
    print(f"✅ URL de Postgres detectada en .env")

if not os.path.exists(SQLITE_DB):
    print(f"❌ Base de datos SQLite {SQLITE_DB} no encontrada.")
    sys.exit(1)

print("\n🔗 Conectando a las bases de datos...")

# Connect to SQLite
try:
    conn_sqlite = sqlite3.connect(SQLITE_DB)
    conn_sqlite.row_factory = sqlite3.Row
    cur_sqlite = conn_sqlite.cursor()
    print("✅ Conectado a SQLite")
except Exception as e:
    print(f"❌ Error conectando a SQLite: {e}")
    sys.exit(1)

# Connect to Postgres
try:
    conn_pg = psycopg2.connect(PG_URL)
    cur_pg = conn_pg.cursor()
    print("✅ Conectado a PostgreSQL (Neon)")
except Exception as e:
    print(f"❌ Error al conectar a Postgres: {e}")
    conn_sqlite.close()
    sys.exit(1)

# 1. Ensure Schema
print("\n🏗️  Verificando/Creando estructura de la base de datos...")
if os.path.exists('init_postgres.sql'):
    try:
        with open('init_postgres.sql', 'r', encoding='utf-8') as f:
            sql_schema = f.read()
        cur_pg.execute(sql_schema)
        conn_pg.commit()
        print("✅ Tablas creadas/verificadas correctamente (init_postgres.sql).")
    except Exception as e:
        conn_pg.rollback()
        print(f"❌ Error al ejecutar init_postgres.sql: {e}")
        # Continue anyway? Maybe user wants to just migrate data to existing tables.
        prompt = input("⚠️  ¿Desea continuar con la migración de datos a pesar del error de esquema? (s/n): ")
        if prompt.lower() != 's':
            sys.exit(1)
else:
    print("⚠️  init_postgres.sql no encontrado. Asumiendo que las tablas ya existen.")

# Helper to get columns
def get_sqlite_columns(table_name):
    try:
        cur_sqlite.execute(f"PRAGMA table_info({table_name})")
        return [row['name'] for row in cur_sqlite.fetchall()]
    except:
        return []

def get_pg_columns(table_name):
    try:
        cur_pg.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table_name,))
        return [row[0] for row in cur_pg.fetchall()]
    except:
        return []

# 2. Migration Function
def migrate_table(table, conflict_target='id'):
    print(f"\n📦 Procesando tabla: {table}")
    
    # Get columns
    sqlite_cols = get_sqlite_columns(table)
    pg_cols = get_pg_columns(table)
    
    if not sqlite_cols:
        print(f"  ⚠️  La tabla source '{table}' no existe o está vacía en SQLite. Saltando.")
        return
    
    if not pg_cols:
        print(f"  ⚠️  La tabla destino '{table}' no existe en Postgres. Saltando.")
        return

    # Find common columns
    common_cols = list(set(sqlite_cols) & set(pg_cols))
    
    if not common_cols:
        print(f"  ❌ No hay columnas comunes entre SQLite y Postgres para '{table}'.")
        return
        
    print(f"  📝 Columnas a migrar: {', '.join(common_cols)}")
    
    # Read from SQLite
    try:
        cur_sqlite.execute(f"SELECT {', '.join(common_cols)} FROM {table}")
        rows = cur_sqlite.fetchall()
    except Exception as e:
        print(f"  ❌ Error leyendo {table} de SQLite: {e}")
        return

    total_rows = len(rows)
    print(f"  Encontrados {total_rows} registros en SQLite.")
    
    if total_rows == 0:
        return

    # Prepare SQL Insert
    cols_sql = sql.SQL(', ').join(map(sql.Identifier, common_cols))
    placeholders = sql.SQL(', ').join(sql.Placeholder() * len(common_cols))
    
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO NOTHING").format(
        sql.Identifier(table),
        cols_sql,
        placeholders,
        sql.Identifier(conflict_target)
    )

    success = 0
    errors = 0
    deferred_rows = []
    
    # Insert row by row
    for row in rows:
        row_data = list(row)
        # Handle boolean conversion if needed (SQLite 0/1 -> PG boolean)
        # But usually psycopg2 handles it well if schema matches. 
        # Checking specific columns might be needed if types differ drastically.
        
        try:
            cur_pg.execute(insert_query, row_data)
            if cur_pg.rowcount > 0:
                success += 1
        except psycopg2.errors.ForeignKeyViolation:
            conn_pg.rollback()
            deferred_rows.append(row_data)
        except Exception as e:
            conn_pg.rollback()
            print(f"  ❌ Error en fila: {e}")
            errors += 1
        else:
            conn_pg.commit()
            
    # Retry deferred rows
    if deferred_rows:
        print(f"  🔄 Reintentando {len(deferred_rows)} filas pospuestas (posibles dependencias FK)...")
        for row_data in deferred_rows:
            try:
                cur_pg.execute(insert_query, row_data)
                if cur_pg.rowcount > 0:
                    success += 1
                conn_pg.commit()
            except Exception as e:
                conn_pg.rollback()
                # print(f"  ❌ Falló reintento: {e}")
                errors += 1
                
    print(f"  ✅ Completado: {success} insertados, {total_rows - success - errors} omitidos (ya existían), {errors} errores.")

    # Reset Sequence
    if 'id' in common_cols and success > 0:
        try:
            cur_pg.execute(sql.SQL("SELECT setval(pg_get_serial_sequence({}, 'id'), COALESCE(MAX(id), 0) + 1, false) FROM {}").format(sql.Identifier(table), sql.Identifier(table)))
            conn_pg.commit()
        except:
            conn_pg.rollback()

# Tables ordered by dependency
tables_to_migrate = [
    ('branches', 'id'),
    ('users', 'id'),
    ('employees', 'id'),
    ('attendance_roster', 'employee_id'), # Conflict target is unique constraint
    ('incidents', 'id'),
    ('attendance', 'id'), # Conflict target might be (employee_id, date) but 'id' is PK
    ('reports', 'id')     # Conflict target unique(employee_id, month, year) but 'id' is PK
]

# Adjust conflict targets for tables where ID might not be the only constraint causing conflicts
# But usually ON CONFLICT DO NOTHING works if *any* constraint is violated? 
# No, requires specifying the constraint column/index.
# Postgres requires `ON CONFLICT (col)`.
# attendance_roster has UNIQUE(employee_id).
# attendance has UNIQUE(employee_id, date).
# reports has UNIQUE(employee_id, month, year).
# `users` has UNIQUE(username).

# Enhanced table list with specific conflict targets
tables_config = [
    ('branches', 'id'),
    ('users', 'username'), # Users unique by username usually
    ('employees', 'id'),
    ('attendance_roster', 'employee_id'),
    ('incidents', 'id'),
    ('attendance', 'id'), # Or 'employee_id, date' depending on index. Let's use ID if we migrating IDs.
    ('reports', 'id')
]

# But wait, if we are migrating IDs, we should conflict on ID.
# If IDs mismatch, we have a problem.
# Let's stick to ID for primary keys.
# Exception: `attendance_roster` might not have ID in some schema versions? `init_postgres` says `id SERIAL PRIMARY KEY`.

print("\n🚀 Iniciando Migración de Datos...")

for t_name, t_conflict in tables_config:
    # Special handling for tables where we want to ensure we don't duplicate by logical key
    # If the user wants to keep IDs, we conflict on ID.
    migrate_table(t_name, 'id' if t_name not in ['attendance_roster'] else 'employee_id') 
    # Note: attendance_roster PK is id, but unique is employee_id. 
    # If we migrate data with IDs, we conflict on ID. 
    # If we don't transfer IDs, we conflict on logical key.
    # The script gets ALL common columns, including ID.
    # So we should conflict on ID.

print("\n✨ Migración finalizada.")
cur_pg.close()
conn_pg.close()
conn_sqlite.close()
