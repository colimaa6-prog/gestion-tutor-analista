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
    console.log('\n--- SCHEMA: incidents ---');
    db.all("PRAGMA table_info(incidents)", (err, columns) => {
        if (err) {
            console.error('Error getting incidents schema:', err.message);
        } else {
            console.table(columns);
        }
    });
});

db.close();
