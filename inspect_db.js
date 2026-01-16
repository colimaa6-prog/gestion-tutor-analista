const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'gestion_tutor.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database ' + dbPath + ': ' + err.message);
        process.exit(1);
    }
    console.log('Connected to the SQLite database.');
});

db.serialize(() => {
    // List all tables
    db.all("SELECT name FROM sqlite_master WHERE type='table'", (err, tables) => {
        if (err) {
            console.error('Error getting tables:', err.message);
            return;
        }
        console.log('\n--- TABLES IN DATABASE ---');
        console.table(tables);

        // Inspect 'attendance' table specifically
        console.log('\n--- SCHEMA: attendance ---');
        db.all("PRAGMA table_info(attendance)", (err, columns) => {
            if (err) {
                console.error('Error getting attendance schema:', err.message);
            } else {
                console.table(columns);
            }
        });

        // Inspect 'users' table specifically if interested
        console.log('\n--- SCHEMA: users ---');
        db.all("PRAGMA table_info(users)", (err, columns) => {
            if (err) {
                console.error('Error getting users schema:', err.message);
            } else {
                console.table(columns);
            }
            db.close((err) => {
                if (err) {
                    console.error(err.message);
                }
                console.log('\nClose the database connection.');
            });
        });
    });
});
