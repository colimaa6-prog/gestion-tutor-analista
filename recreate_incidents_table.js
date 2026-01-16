const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'gestion_tutor.db');
const db = new sqlite3.Database(dbPath);

const createTableQuery = `
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_id INTEGER NOT NULL,
    reported_by INTEGER NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'EN PROCESO',
    start_date DATE,
    end_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (reported_by) REFERENCES employees(id)
)
`;

db.serialize(() => {
    // 1. Drop existing table
    console.log('Dropping table incidents...');
    db.run("DROP TABLE IF EXISTS incidents", (err) => {
        if (err) {
            console.error('Error dropping table:', err.message);
            return;
        }
        console.log('Table dropped.');

        // 2. Create new table
        console.log('Creating new table incidents...');
        db.run(createTableQuery, (err) => {
            if (err) {
                console.error('Error creating table:', err.message);
            } else {
                console.log('Table created successfully with updated schema.');
            }
            db.close(() => {
                console.log('Database connection closed.');
            });
        });
    });
});
