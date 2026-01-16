const db = require('./database');

console.log('Starting users table schema update...');

db.serialize(() => {
    // Add supervisor_id column to users table
    db.run(`
        ALTER TABLE users 
        ADD COLUMN supervisor_id INTEGER 
        REFERENCES users(id)
    `, (err) => {
        if (err) {
            if (err.message.includes('duplicate column name')) {
                console.log('✓ Column supervisor_id already exists');
            } else {
                console.error('Error adding supervisor_id column:', err);
                process.exit(1);
            }
        } else {
            console.log('✓ Added supervisor_id column to users table');
        }

        // Verify the schema
        db.all("PRAGMA table_info(users)", [], (err, rows) => {
            if (err) {
                console.error('Error checking schema:', err);
            } else {
                console.log('\n✓ Current users table schema:');
                rows.forEach(col => {
                    console.log(`  - ${col.name} (${col.type})`);
                });
            }

            db.close((err) => {
                if (err) {
                    console.error('Error closing database:', err);
                } else {
                    console.log('\n✓ Schema update completed successfully!');
                }
            });
        });
    });
});
