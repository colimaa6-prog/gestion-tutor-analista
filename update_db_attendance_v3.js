const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'gestion_tutor.db');
const db = new sqlite3.Database(dbPath);

const columnsToAdd = [
    { name: 'start_date', type: 'TEXT' }
];

db.serialize(() => {
    columnsToAdd.forEach(col => {
        const sql = `ALTER TABLE attendance ADD COLUMN ${col.name} ${col.type}`;
        db.run(sql, (err) => {
            if (err) {
                if (err.message.includes('duplicate column name')) {
                    console.log(`Column ${col.name} already exists.`);
                } else {
                    console.error(`Error adding column ${col.name}:`, err.message);
                }
            } else {
                console.log(`Added column ${col.name}`);
            }
        });
    });
});

db.close();
