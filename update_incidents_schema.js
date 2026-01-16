const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'gestion_tutor.db');
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
    // Add start_date column
    db.run("ALTER TABLE incidents ADD COLUMN start_date DATE", (err) => {
        if (err && err.message.includes('duplicate column name')) {
            console.log('Column start_date already exists.');
        } else if (err) {
            console.error('Error adding start_date:', err.message);
        } else {
            console.log('Column start_date added successfully.');
        }
    });

    // Add end_date column
    db.run("ALTER TABLE incidents ADD COLUMN end_date DATE", (err) => {
        if (err && err.message.includes('duplicate column name')) {
            console.log('Column end_date already exists.');
        } else if (err) {
            console.error('Error adding end_date:', err.message);
        } else {
            console.log('Column end_date added successfully.');
        }
    });
});

db.close(() => {
    console.log('Schema update complete.');
});
