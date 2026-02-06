
import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def run_migration():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not set in environment or .env file.")
        return

    print(f"Connecting to database: {DATABASE_URL.split('@')[-1]}") # Print host only for privacy
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Adding birth_date column to employees table...")
        cursor.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS birth_date DATE;")
        
        conn.commit()
        conn.close()
        print("Migration successful: birth_date column added.")
        
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    run_migration()
