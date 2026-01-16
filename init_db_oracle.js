const db = require('./database_oracle');
const fs = require('fs');
const path = require('path');

const schemaPath = path.join(__dirname, 'schema_oracle.sql');
const schema = fs.readFileSync(schemaPath, 'utf8');

console.log('Running Oracle Schema script...');

(async () => {
    try {
        await db.execScript(schema);
        console.log('Schema setup complete.');
    } catch (e) {
        console.error('Error running schema:', e);
    }
})();
