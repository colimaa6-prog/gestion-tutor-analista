const db = require('./database');

console.log('Adding added_by_user_id column to attendance_roster...');

// Add column if it doesn't exist
db.run(`
    ALTER TABLE attendance_roster 
    ADD COLUMN added_by_user_id INTEGER REFERENCES users(id)
`, (err) => {
    if (err) {
        if (err.message.includes('duplicate column')) {
            console.log('✓ Column already exists');
        } else {
            console.error('Error:', err.message);
        }
    } else {
        console.log('✓ Column added successfully');
    }

    db.close();
});
