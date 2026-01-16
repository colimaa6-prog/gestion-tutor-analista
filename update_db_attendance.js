const db = require('./database');

console.log('--- Actualizando Base de Datos (Asistencias) ---');

db.serialize(() => {
    // Table for storing daily attendance
    db.run(`
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL, -- YYYY-MM-DD
            status TEXT NOT NULL, -- present, delay, absent, vacation, permission, incapacity
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    `, (err) => {
        if (err) console.error('Error creando tabla attendance:', err);
        else console.log('✅ Tabla "attendance" verificada/creada.');
    });

    // We also need a way to store "which employees are visible in the grid" for the custom list requirement.
    // Let's create a "attendance_roster" table.
    db.run(`
        CREATE TABLE IF NOT EXISTS attendance_roster (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    `, (err) => {
        if (err) console.error('Error creando tabla attendance_roster:', err);
        else console.log('✅ Tabla "attendance_roster" verificada/creada.');
    });
});
