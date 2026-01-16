const db = require('./database');

// Script to add new columns to attendance table
const alterTableSQL = `
-- Add new columns to attendance table
ALTER TABLE attendance ADD COLUMN comment TEXT;
ALTER TABLE attendance ADD COLUMN arrival_time TEXT;
ALTER TABLE attendance ADD COLUMN permission_type TEXT;
ALTER TABLE attendance ADD COLUMN start_date DATE;
ALTER TABLE attendance ADD COLUMN end_date DATE;
`;

console.log('Updating attendance table schema...');

// SQLite doesn't support multiple ALTER TABLE in one exec, so we do them separately
const alterCommands = [
    "ALTER TABLE attendance ADD COLUMN comment TEXT",
    "ALTER TABLE attendance ADD COLUMN arrival_time TEXT",
    "ALTER TABLE attendance ADD COLUMN permission_type TEXT",
    "ALTER TABLE attendance ADD COLUMN start_date DATE",
    "ALTER TABLE attendance ADD COLUMN end_date DATE"
];

db.serialize(() => {
    alterCommands.forEach((cmd, index) => {
        db.run(cmd, (err) => {
            if (err) {
                // Column might already exist, that's okay
                if (err.message.includes('duplicate column name')) {
                    console.log(`Column ${index + 1} already exists, skipping...`);
                } else {
                    console.error(`Error on command ${index + 1}:`, err.message);
                }
            } else {
                console.log(`✓ Added column ${index + 1} successfully`);
            }
        });
    });

    // Verify the changes
    setTimeout(() => {
        db.all("PRAGMA table_info(attendance)", [], (err, rows) => {
            if (err) {
                console.error('Error checking table:', err);
            } else {
                console.log('\nCurrent attendance table structure:');
                rows.forEach(col => {
                    console.log(`  - ${col.name} (${col.type})`);
                });
                console.log('\nSchema update complete!');
                db.close();
            }
        });
    }, 500);
});
