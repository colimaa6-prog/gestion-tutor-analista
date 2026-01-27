
import psycopg2
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

DEST_URL = "postgresql://neondb_owner:npg_cN56UidePSJM@ep-fancy-band-ahpwdako-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

try:
    conn = psycopg2.connect(DEST_URL)
    cur = conn.cursor()
    
    tables = ['branches', 'users', 'employees', 'attendance_roster', 'incidents', 'attendance', 'reports']
    
    print("--- Recuento de filas en NEON ---")
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            count = cur.fetchone()[0]
            print(f"{t}: {count} filas")
        except Exception as e:
            print(f"{t}: Error ({e})")
            conn.rollback()
            
    conn.close()

except Exception as e:
    print(f"Error conectando: {e}")
