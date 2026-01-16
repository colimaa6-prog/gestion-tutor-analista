const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./gestion_tutor.db');

console.log('=== Inspecting REPORTS table ===\n');

// Get table schema
db.all("PRAGMA table_info(reports)", (err, rows) => {
    if (err) {
        console.error("Error getting table info:", err.message);
        return;
    }

    console.log('Table Schema:');
    console.log('-------------');
    rows.forEach(row => {
        console.log(`${row.name} (${row.type}) ${row.notnull ? 'NOT NULL' : ''} ${row.pk ? 'PRIMARY KEY' : ''} ${row.dflt_value ? 'DEFAULT ' + row.dflt_value : ''}`);
    });

    console.log('\n');

    // Get row count
    db.get("SELECT COUNT(*) as count FROM reports", (err, row) => {
        if (err) {
            console.error("Error counting rows:", err.message);
        } else {
            console.log(`Total records: ${row.count}`);
        }

        // Get sample data if any exists
        db.all("SELECT * FROM reports LIMIT 5", (err, rows) => {
            if (err) {
                console.error("Error getting sample data:", err.message);
            } else if (rows.length > 0) {
                console.log('\nSample Data:');
                console.log('------------');
                console.log(rows);
            } else {
                console.log('\nNo data in table yet.');
            }

            db.close();
        });
    });
});
