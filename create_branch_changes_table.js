require('dotenv').config();
const { Client } = require('pg');

async function createBranchChangesTable() {
    const client = new Client({
        connectionString: process.env.DATABASE_URL,
        ssl: {
            rejectUnauthorized: false
        }
    });

    try {
        await client.connect();
        console.log('✅ Conectado a Neon PostgreSQL');

        // Crear tabla
        await client.query(`
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
        `);
        console.log('✅ Tabla branch_changes creada');

        // Crear índices
        await client.query(`
            CREATE INDEX IF NOT EXISTS idx_branch_changes_processed ON branch_changes(processed);
        `);
        console.log('✅ Índice idx_branch_changes_processed creado');

        await client.query(`
            CREATE INDEX IF NOT EXISTS idx_branch_changes_created ON branch_changes(created_at);
        `);
        console.log('✅ Índice idx_branch_changes_created creado');

        // Insertar un registro de prueba
        await client.query(`
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
        `);
        console.log('✅ Registro de prueba insertado');

        console.log('\n🎉 ¡Tabla branch_changes creada exitosamente!');

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await client.end();
    }
}

createBranchChangesTable();
