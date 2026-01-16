const db = require('./database');

console.log('Updating existing roster entries with added_by_user_id...');

// Get all users
db.all('SELECT id, username FROM users', [], (err, users) => {
    if (err) {
        console.error('Error fetching users:', err);
        db.close();
        return;
    }

    console.log(`Found ${users.length} users`);

    // For each user, update roster entries that don't have added_by_user_id
    let updated = 0;
    let processed = 0;

    users.forEach((user, index) => {
        db.run(
            `UPDATE attendance_roster 
             SET added_by_user_id = ? 
             WHERE added_by_user_id IS NULL 
             AND employee_id IN (SELECT id FROM employees LIMIT 1 OFFSET ?)`,
            [user.id, index],
            function (err) {
                processed++;
                if (err) {
                    console.error(`Error updating for user ${user.username}:`, err.message);
                } else if (this.changes > 0) {
                    console.log(`✓ Assigned ${this.changes} employees to ${user.username}`);
                    updated += this.changes;
                }

                if (processed === users.length) {
                    console.log(`\n✅ Total updated: ${updated} roster entries`);
                    db.close();
                }
            }
        );
    });
});
