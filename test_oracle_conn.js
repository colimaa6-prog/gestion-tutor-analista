const oracledb = require('oracledb');
require('dotenv').config();

console.log('Testing Oracle Connection...');
console.log('User:', process.env.ORACLE_USER ? 'SET' : 'MISSING');
console.log('TNS_ADMIN:', process.env.TNS_ADMIN ? 'SET' : 'MISSING');
console.log('Connect String:', process.env.ORACLE_CONN_STR ? 'SET' : 'MISSING');
console.log('Password has changed:', process.env.ORACLE_PASSWORD && process.env.ORACLE_PASSWORD !== 'password');

async function test() {
    let conn;
    try {
        // Oracle Thin Mode is enabled automatically when initOracleClient is NOT called.
        console.log('Using Oracle Thin Mode (Default)');

        // Connect
        const dbConfig = {
            user: process.env.ORACLE_USER,
            password: process.env.ORACLE_PASSWORD,
            connectString: process.env.ORACLE_CONN_STR
        };
        // Explicitly set wallet location for mTLS
        if (process.env.TNS_ADMIN) {
            dbConfig.walletLocation = process.env.TNS_ADMIN;
        }



        if (process.env.WALLET_PASSWORD) {
            // dbConfig.walletPassword = process.env.WALLET_PASSWORD;
            // Commented out to test cwallet.sso autologin compatibility
        }

        conn = await oracledb.getConnection(dbConfig);
        console.log('SUCCESS! Connected to Oracle Database.');

        // Simple query
        const result = await conn.execute("SELECT 1 FROM DUAL");
        console.log('Query result:', result.rows);

    } catch (err) {
        console.error('CONNECTION FAILED:', err.message);
        process.exit(1);
    } finally {
        if (conn) {
            try { await conn.close(); } catch (e) { }
        }
    }
}

test();
