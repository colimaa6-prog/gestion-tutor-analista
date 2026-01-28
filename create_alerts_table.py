
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def create_alerts_table():
    if not DATABASE_URL:
        print("DATABASE_URL no encontrada en .env")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        print("Creando tabla alerts...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                details TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );
        """)
        conn.commit()
        print("Tabla alerts creada exitosamente.")
    except Exception as e:
        print(f"Error creando tabla: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_alerts_table()
