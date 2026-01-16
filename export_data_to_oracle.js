const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

const dbPath = path.resolve(__dirname, 'gestion_tutor.db');
const db = new sqlite3.Database(dbPath);

let sqlOutput = `-- =====================================================================
-- DATOS MIGRADOS DE SQLITE A ORACLE
-- =====================================================================
-- Generado automáticamente
-- Fecha: ${new Date().toISOString()}
-- =====================================================================

`;

async function exportTable(tableName, columns) {
    return new Promise((resolve, reject) => {
        db.all(`SELECT * FROM ${tableName}`, [], (err, rows) => {
            if (err) {
                console.error(`Error exporting ${tableName}:`, err);
                resolve('');
                return;
            }

            if (rows.length === 0) {
                console.log(`✓ ${tableName}: 0 registros`);
                resolve('');
                return;
            }

            let sql = `\n-- Tabla: ${tableName} (${rows.length} registros)\n`;

            rows.forEach(row => {
                const values = columns.map(col => {
                    const val = row[col];
                    if (val === null || val === undefined) return 'NULL';
                    if (typeof val === 'number') return val;
                    if (typeof val === 'string') {
                        // Escapar comillas simples
                        return `'${val.replace(/'/g, "''")}'`;
                    }
                    return `'${val}'`;
                }).join(', ');

                sql += `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES (${values});\n`;
            });

            console.log(`✓ ${tableName}: ${rows.length} registros exportados`);
            resolve(sql);
        });
    });
}

(async () => {
    console.log('Exportando datos de SQLite...\n');

    // Exportar en orden de dependencias
    sqlOutput += await exportTable('users', ['username', 'password_hash', 'role', 'supervisor_id', 'branch_id']);
    sqlOutput += await exportTable('employees', ['full_name', 'branch_id', 'hire_date', 'status']);
    sqlOutput += await exportTable('incidents', ['branch_id', 'reported_by', 'type', 'status', 'description', 'start_date', 'end_date']);
    sqlOutput += await exportTable('attendance_roster', ['employee_id', 'added_by_user_id']);
    sqlOutput += await exportTable('attendance', ['employee_id', 'date', 'status', 'comment', 'arrival_time', 'permission_type', 'start_date', 'end_date']);
    sqlOutput += await exportTable('reports', ['employee_id', 'month', 'year', 'data']);

    sqlOutput += '\nCOMMIT;\n';
    sqlOutput += '\nPROMPT ✅ Datos importados exitosamente\n';

    // Guardar archivo
    const outputPath = path.resolve(__dirname, 'data_migration_oracle.sql');
    fs.writeFileSync(outputPath, sqlOutput, 'utf8');

    console.log(`\n✅ Archivo generado: data_migration_oracle.sql`);
    console.log('📋 Ejecuta este archivo en Oracle Cloud después de schema_oracle_migration.sql');

    db.close();
})();
