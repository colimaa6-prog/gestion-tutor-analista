const oracledb = require('oracledb');
require('dotenv').config();

// Enable Thin Mode
// Oracle Thin Mode is enabled automatically when initOracleClient is NOT called.
// We rely on process.env.TNS_ADMIN for wallet location.
console.log('Using Oracle Thin Mode (Default)');

const dbConfig = {
    user: process.env.ORACLE_USER,
    password: process.env.ORACLE_PASSWORD,
    connectString: process.env.ORACLE_CONN_STR
};
if (process.env.TNS_ADMIN) {
    dbConfig.walletLocation = process.env.TNS_ADMIN;
}


if (process.env.WALLET_PASSWORD) {
    dbConfig.walletPassword = process.env.WALLET_PASSWORD;
}

async function getConn() {
    return await oracledb.getConnection(dbConfig);
}

// Helper to convert ? placeholders to :1, :2, etc.
function convertSql(sql) {
    let i = 0;
    return sql.replace(/\?/g, () => `:${++i}`);
}

const db = {
    // Emulate sqlite3 db.all
    all: async function (sql, params, callback) {
        if (typeof params === 'function') {
            callback = params;
            params = [];
        }

        let conn;
        try {
            conn = await getConn();
            const oracleSql = convertSql(sql);
            const result = await conn.execute(oracleSql, params || [], {
                outFormat: oracledb.OUT_FORMAT_OBJECT
            });

            // Lowercase keys to match sqlite behavior usually (or ensure server.js handles case)
            // Oracle returns UPPERCASE col names by default in OBJECT mode.
            // We should convert to lowercase for compatibility.
            const rows = result.rows.map(row => {
                const newRow = {};
                for (const key in row) {
                    newRow[key.toLowerCase()] = row[key];
                }
                return newRow;
            });

            callback(null, rows);
        } catch (err) {
            callback(err);
        } finally {
            if (conn) {
                try { await conn.close(); } catch (e) { console.error(e); }
            }
        }
    },

    // Emulate sqlite3 db.get
    get: async function (sql, params, callback) {
        if (typeof params === 'function') {
            callback = params;
            params = [];
        }

        this.all(sql, params, (err, rows) => {
            if (err) return callback(err);
            callback(null, rows[0]);
        });
    },

    // Emulate sqlite3 db.run
    run: async function (sql, params, callback) {
        if (typeof params === 'function') {
            callback = params;
            params = [];
        }

        let conn;
        try {
            conn = await getConn();
            let oracleSql = convertSql(sql);

            // Handle LIMIT/OFFSET if present (simple regex, might need more robust logic)
            // SQLite: LIMIT ? OFFSET ? -> Oracle: OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            // But typically specific queries used in server.js need check.

            // Check for INSERT to handle lastID
            // This is tricky. For now, we return dummy lastID unless we modify the SQL.
            // We will trust server.js modifications for critical inserts.

            // Special handling for INSERT OR IGNORE -> MERGE or Exception handling
            if (oracleSql.includes('INSERT OR IGNORE')) {
                // Oracle doesn't have INSERT OR IGNORE. 
                // Simple hack: Remove "OR IGNORE" and let it fail, catch unique constraint?
                // Or use MERGE.
                // For now: Just try INSERT and ignore specific error.
                oracleSql = oracleSql.replace('INSERT OR IGNORE', 'INSERT');
            }

            // SQLite: INSERT OR REPLACE -> MERGE in Oracle?
            if (oracleSql.includes('INSERT OR REPLACE')) {
                // This is complex to emulate automatically.
                // We should flag this for server.js updates.
                // For now, replace with INSERT (and fail) or similar? 
                // Replacing with "MERGE" requires knowing keys. 
                // Let's assume user logic needs update for this.
                console.warn('WARNING: INSERT OR REPLACE not fully supported in shim.');
                oracleSql = oracleSql.replace('INSERT OR REPLACE', 'INSERT');
            }

            const result = await conn.execute(oracleSql, params || [], {
                autoCommit: true,
            });

            // Simulate "this" context
            const context = {
                lastID: 0, // Not supported automatically without RETURNING
                changes: result.rowsAffected
            };

            callback.call(context, null);
        } catch (err) {
            // If we stripped OR IGNORE, suppress unique constraint error (ORA-00001)
            if (sql.includes('INSERT OR IGNORE') && err.message.includes('ORA-00001')) {
                const context = { lastID: 0, changes: 0 };
                return callback.call(context, null);
            }

            callback(err);
        } finally {
            if (conn) {
                try { await conn.close(); } catch (e) { console.error(e); }
            }
        }
    },

    // Helper to run scripts (for schema)
    execScript: async function (script) {
        let conn;
        try {
            conn = await getConn();
            const statements = script.split(';').filter(s => s.trim().length > 0);
            for (const stmt of statements) {
                try {
                    await conn.execute(stmt);
                } catch (e) {
                    console.error('Script Error on:', stmt, e.message);
                }
            }
        } catch (err) {
            console.error(err);
        } finally {
            if (conn) await conn.close();
        }
    }
};

module.exports = db;
