const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'gestion_tutor.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
        process.exit(1);
    }
});

db.all("SELECT id, username, role FROM users", [], (err, rows) => {
    if (err) {
        throw err;
    }
    console.log("Active Users:");
    rows.forEach((row) => {
        console.log(`${row.id}: ${row.username} - ${row.role}`);
    });
    db.close();
});
