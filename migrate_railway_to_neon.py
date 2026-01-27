
import psycopg2
from psycopg2 import sql
import os
import sys
from dotenv import load_dotenv

# Force UTF-8 for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# 1. Source: Railway (current DATABASE_URL in .env)
SOURCE_URL = os.getenv('DATABASE_URL')
# 2. Destination: Neon (user must provide)
DEST_URL = None

print("="*60)
print("🚂 -> 🟢  MIGRACIÓN DE RAILWAY A NEON (POSTGRES A POSTGRES)")
print("="*60)

if not SOURCE_URL:
    print("❌ No se encontró DATABASE_URL de Railway en el archivo .env")
    SOURCE_URL = input("👉 Introduce la URL de RAILWAY (Origen): ").strip()
else:
    print(f"✅ URL de Origen (Railway) detectada en .env: {SOURCE_URL[:40]}...")

print("\nAhora necesitamos la URL de la nueva base de datos (Neon).")
DEST_URL = input("👉 Introduce la URL de NEON (Destino): ").strip()

if not SOURCE_URL or not DEST_URL:
    print("❌ Se requieren ambas URLs. Saliendo.")
    sys.exit(1)

print("\n🔗 Conectando a las bases de datos...")

try:
    # Source Connection
    conn_src = psycopg2.connect(SOURCE_URL)
    cur_src = conn_src.cursor()
    print("✅ Conectado a RAILWAY (Origen)")
    
    # Destination Connection
    conn_dest = psycopg2.connect(DEST_URL)
    cur_dest = conn_dest.cursor()
    print("✅ Conectado a NEON (Destino)")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
    sys.exit(1)

# List of tables to migrate in dependency order
TABLES = [
    'branches',
    'users',
    'employees',
    'attendance_roster',
    'incidents',
    'attendance',
    'reports'
]

# 1. Ensure Schema
print("\n🏗️  Verificando/Creando estructura en NEON...")
if os.path.exists('init_postgres.sql'):
    try:
        with open('init_postgres.sql', 'r', encoding='utf-8') as f:
            sql_schema = f.read()
        cur_dest.execute(sql_schema)
        conn_dest.commit()
        print("✅ Esquema base aplicado en Neon.")
    except Exception as e:
        conn_dest.rollback()
        print(f"⚠️  Advertencia al aplicar esquema: {e}")
else:
    print("⚠️  init_postgres.sql no encontrado. Asumiendo que las tablas ya existen.")

def migrate_table_data(table_name):
    print(f"\n📦 Migrando datos de tabla: {table_name}")
    
    # Get columns from Source to ensure we map correctly
    try:
        cur_src.execute(f"SELECT * FROM {table_name} LIMIT 0")
        colnames = [desc[0] for desc in cur_src.description]
        
        # Check if table exists in Dest
        cur_dest.execute(f"SELECT to_regclass('{table_name}')")
        if not cur_dest.fetchone()[0]:
            print(f"  ❌ Tabla {table_name} no existe en destino. Saltando.")
            return

        # Read data
        # Construct query with explicit column names
        cols_str = ', '.join([f'"{c}"' for c in colnames])
        cur_src.execute(f'SELECT {cols_str} FROM "{table_name}"')
        rows = cur_src.fetchall()
        
        print(f"  📥 Leyendo {len(rows)} filas de Railway...")
        
        if not rows:
            return

        # Generate INSERT query
        placeholders = ', '.join(['%s'] * len(colnames))
        # Handle conflicts: Try ON CONFLICT DO NOTHING based on ID if present
        conflict_clause = ""
        if 'id' in colnames:
            conflict_clause = 'ON CONFLICT ("id") DO NOTHING'
        elif table_name == 'attendance_roster':
             conflict_clause = 'ON CONFLICT ("employee_id") DO NOTHING'
        elif table_name == 'reports':
             conflict_clause = 'ON CONFLICT ("employee_id", "month", "year") DO NOTHING'
        
        insert_query = f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders}) {conflict_clause}'
        
        success_count = 0
        error_count = 0
        
        for row in rows:
            try:
                cur_dest.execute(insert_query, row)
                if cur_dest.rowcount > 0:
                    success_count += 1
            except psycopg2.errors.UniqueViolation:
                conn_dest.rollback()
                # Already exists
            except psycopg2.errors.ForeignKeyViolation:
                conn_dest.rollback()
                print(f"  ⚠️  Error FK para fila (posiblemente falta la dependencia): {row}")
                error_count += 1
            except Exception as e:
                conn_dest.rollback()
                print(f"  ❌ Error insertando: {e}")
                error_count += 1
            else:
                conn_dest.commit()
        
        print(f"  ✅ {success_count} filas insertadas. {len(rows) - success_count - error_count} duplicados omitidos.")

        # Reset sequences
        if 'id' in colnames:
            try:
                cur_dest.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM {table_name}")
                conn_dest.commit()
            except:
                conn_dest.rollback()

    except Exception as e:
        print(f"  ❌ Error general con tabla {table_name}: {e}")
        conn_src.rollback()
        conn_dest.rollback()

print("\n🚀 Iniciando transferencia de datos...")

for table in TABLES:
    migrate_table_data(table)

print("\n✨ Migración de RAILWAY -> NEON completada.")
cur_src.close()
conn_src.close()
cur_dest.close()
conn_dest.close()
