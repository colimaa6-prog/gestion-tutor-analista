
import psycopg2
from psycopg2 import sql
import os
import sys
from dotenv import load_dotenv

# Force UTF-8 for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# 1. Source: Railway
SOURCE_URL = os.getenv('DATABASE_URL')

# 2. Destination: Neon (Provided by user)
DEST_URL = "postgresql://neondb_owner:npg_cN56UidePSJM@ep-fancy-band-ahpwdako-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

print("="*60)
print("🚂 -> 🟢  MIGRACIÓN DE RAILWAY A NEON (AUTOMÁTICA)")
print("="*60)

if not SOURCE_URL:
    print("❌ No se encontró DATABASE_URL de Railway en el archivo .env")
    sys.exit(1)

print(f"✅ Origen: Railway ({SOURCE_URL[:30]}...)")
print(f"✅ Destino: Neon ({DEST_URL[:30]}...)")

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
print("\n🏗️  Verificando estructura en NEON...")
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
    print("⚠️  init_postgres.sql no encontrado.")

def clean_value(val):
    if hasattr(val, 'isoformat'):
        return val.isoformat()
    return val

def migrate_table_data(table_name):
    print(f"\n📦 Migrando datos de tabla: {table_name}")
    
    try:
        # Check source cols
        cur_src.execute(f"SELECT * FROM {table_name} LIMIT 0")
        colnames = [desc[0] for desc in cur_src.description]
        
        # Build Select
        cols_str = ', '.join([f'"{c}"' for c in colnames])
        cur_src.execute(f'SELECT {cols_str} FROM "{table_name}"')
        rows = cur_src.fetchall()
        
        print(f"  📥 Leyendo {len(rows)} filas de Railway...")
        
        if not rows:
            return

        # Prepare Insert
        placeholders = ', '.join(['%s'] * len(colnames))
        
        insert_query = f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders})'
        
        # Add conflict handling
        # For attendance_roster, the unique constraint is usually employee_id, not ID in some schemas?
        # Let's check init_postgres.sql
        # users: username UNIQUE
        # attendance_roster: UNIQUE(employee_id)
        # reports: UNIQUE(employee_id, month, year)
        # attendance: UNIQUE(employee_id, date)
        
        on_conflict = ""
        if 'id' in colnames:
             on_conflict = 'ON CONFLICT ("id") DO NOTHING'
        
        # Specific overrides for unique constraints if IDs are different or missing (should exist)
        if table_name == 'users':
            on_conflict = 'ON CONFLICT ("username") DO NOTHING' # Prioritize username uniqueness
        elif table_name == 'attendance_roster':
            on_conflict = 'ON CONFLICT ("employee_id") DO NOTHING'
        elif table_name == 'reports':
            on_conflict = 'ON CONFLICT ("employee_id", "month", "year") DO NOTHING'
        elif table_name == 'attendance':
             on_conflict = 'ON CONFLICT ("employee_id", "date") DO NOTHING'
             
        # If ID matches, we want to keep ID.
        # But if we rely on "id" conflict, and sequence is different...
        # We are migrating data, so we want exact ID match.
        if 'id' in colnames:
            on_conflict = 'ON CONFLICT ("id") DO NOTHING'
            
        full_query = f"{insert_query} {on_conflict}"

        success = 0
        errors = 0
        
        for row in rows:
            try:
                cur_dest.execute(full_query, row)
                if cur_dest.rowcount > 0:
                    success += 1
            except psycopg2.errors.ForeignKeyViolation:
                conn_dest.rollback()
                print(f"    ⚠️ FK perdida en registro ID {row[0] if 'id' in colnames else '?'}")
                errors += 1
            except Exception as e:
                conn_dest.rollback()
                print(f"    ❌ Error: {e}")
                errors += 1
            else:
                conn_dest.commit()
                
        print(f"  ✅ {success} insertados. {len(rows) - success - errors} omitidos. {errors} errores.")

        # Reset sequences
        if 'id' in colnames:
            try:
                cur_dest.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM {table_name}")
                conn_dest.commit()
            except:
                conn_dest.rollback()

    except Exception as e:
        print(f"  ❌ Error procesando tabla: {e}")

for table in TABLES:
    migrate_table_data(table)

print("\n✨ Migración finalizada exitosamente.")
cur_src.close()
conn_src.close()
cur_dest.close()
conn_dest.close()
