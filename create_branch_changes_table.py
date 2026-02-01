import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_branch_changes_table():
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print('✅ Conectado a Neon PostgreSQL')
        
        # Crear tabla
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branch_changes (
                id SERIAL PRIMARY KEY,
                branch_id INTEGER REFERENCES branches(id),
                branch_name VARCHAR(200),
                change_type VARCHAR(20) NOT NULL,
                employee_name VARCHAR(200),
                hire_date DATE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                processed_at TIMESTAMP,
                processed_by INTEGER REFERENCES users(id)
            );
        """)
        print('✅ Tabla branch_changes creada')
        
        # Crear índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_branch_changes_processed ON branch_changes(processed);
        """)
        print('✅ Índice idx_branch_changes_processed creado')
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_branch_changes_created ON branch_changes(created_at);
        """)
        print('✅ Índice idx_branch_changes_created creado')
        
        # Insertar un registro de prueba
        cursor.execute("""
            INSERT INTO branch_changes (
                branch_id,
                branch_name,
                change_type,
                employee_name,
                hire_date,
                description
            ) VALUES (
                (SELECT id FROM branches LIMIT 1),
                (SELECT name FROM branches LIMIT 1),
                'ingreso',
                'Juan Pérez Flores',
                '2024-05-25',
                'Actualización: cambio de nombre de colaborador en sucursal Querétaro grupal ctg 1.'
            );
        """)
        print('✅ Registro de prueba insertado')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print('\n🎉 ¡Tabla branch_changes creada exitosamente!')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    create_branch_changes_table()
