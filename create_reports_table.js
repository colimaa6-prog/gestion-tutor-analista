const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./gestion_tutor.db');

// Add timeout to prevent locking
db.configure('busyTimeout', 5000);

db.serialize(() => {
    // Drop logic to ensure clean slate (USER wants to "create" it, implication: reset or fix)
    // Warning: This deletes existing report data. Since it wasn't working, this is likely acceptable.
    // If we wanted to preserve, we'd use ALTER, but the schema is changing fundamentally.
    // db.run("DROP TABLE IF EXISTS reports"); 

    // Actually, let's keep it safe. IF NOT EXISTS.
    // If the schema is different, we might need to handle migration manually or just drop it if empty.
    // Given the user said "no esta creado", we assume it's safe to create.

    // We'll use a single text column 'data' to store the complex JSON structure 
    // { faltantes: {}, guias: {}, tableros: {} }
    const schema = `
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            month INTEGER,
            year INTEGER,
            data TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(id),
            UNIQUE(employee_id, month, year)
        )
    `;

    db.run(schema, (err) => {
        if (err) {
            console.error("Error creating reports table:", err.message);
        } else {
            console.log("Reports table created successfully.");
        }
    });
});

db.close();
