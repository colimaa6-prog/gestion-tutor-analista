const db = require('./database');

console.log('Clearing attendance_roster table...');

db.run('DELETE FROM attendance_roster', [], function (err) {
    if (err) {
        console.error('Error:', err.message);
    } else {
        console.log(`✓ Deleted ${this.changes} roster entries`);
        console.log('✅ Roster cleared. Users can now add employees again.');
    }
    db.close();
});
