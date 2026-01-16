const oracledb = require('oracledb');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// Inicializar Oracle Instant Client
if (process.env.ORACLE_INSTANT_CLIENT) {
    try {
        oracledb.initOracleClient({ libDir: process.env.ORACLE_INSTANT_CLIENT });
        console.log('✅ Oracle Instant Client initialized');
    } catch (err) {
        console.error('❌ Error initializing Oracle Instant Client:', err.message);
    }
}

// Configuración de Oracle
oracledb.outFormat = oracledb.OUT_FORMAT_OBJECT;
oracledb.autoCommit = true;

// Configurar Wallet
process.env.TNS_ADMIN = process.env.ORACLE_WALLET_LOCATION;

const dbConfig = {
    user: process.env.ORACLE_USER || 'ADMIN',
    password: process.env.ORACLE_PASSWORD,
    connectString: process.env.ORACLE_CONNECT_STRING || 'reportegestionvn_high'
};

let pool;

async function initialize() {
    try {
        pool = await oracledb.createPool({
            ...dbConfig,
            poolMin: 2,
            poolMax: 10,
            poolIncrement: 1,
            poolTimeout: 60
        });
        console.log('✅ Connected to Oracle Autonomous Database');
    } catch (err) {
        console.error('❌ Error connecting to Oracle:', err);
        throw err;
    }
}

// Wrapper para compatibilidad con SQLite API
const db = {
    // db.run(sql, params, callback)
    run: async function (sql, params = [], callback) {
        let connection;
        try {
            connection = await pool.getConnection();

            // Convertir placeholders ? a :1, :2, etc.
            let oracleSql = sql;
            let paramIndex = 1;
            oracleSql = oracleSql.replace(/\?/g, () => `:${paramIndex++}`);

            const result = await connection.execute(oracleSql, params, { autoCommit: true });

            if (callback) {
                callback.call({ changes: result.rowsAffected, lastID: result.lastRowid }, null);
            }
        } catch (err) {
            console.error('Error in db.run:', err);
            if (callback) callback(err);
        } finally {
            if (connection) {
                try {
                    await connection.close();
                } catch (err) {
                    console.error('Error closing connection:', err);
                }
            }
        }
    },

    // db.get(sql, params, callback)
    get: async function (sql, params = [], callback) {
        let connection;
        try {
            connection = await pool.getConnection();

            // Convertir placeholders
            let oracleSql = sql;
            let paramIndex = 1;
            oracleSql = oracleSql.replace(/\?/g, () => `:${paramIndex++}`);

            const result = await connection.execute(oracleSql, params);

            if (callback) {
                callback(null, result.rows[0] || null);
            }
        } catch (err) {
            console.error('Error in db.get:', err);
            if (callback) callback(err, null);
        } finally {
            if (connection) {
                try {
                    await connection.close();
                } catch (err) {
                    console.error('Error closing connection:', err);
                }
            }
        }
    },

    // db.all(sql, params, callback)
    all: async function (sql, params = [], callback) {
        let connection;
        try {
            connection = await pool.getConnection();

            // Convertir placeholders
            let oracleSql = sql;
            let paramIndex = 1;
            oracleSql = oracleSql.replace(/\?/g, () => `:${paramIndex++}`);

            // Convertir funciones SQLite a Oracle
            oracleSql = oracleSql.replace(/CURRENT_TIMESTAMP/g, 'SYSTIMESTAMP');
            oracleSql = oracleSql.replace(/strftime\('%m', ([^)]+)\)/g, "TO_CHAR($1, 'MM')");
            oracleSql = oracleSql.replace(/strftime\('%Y', ([^)]+)\)/g, "TO_CHAR($1, 'YYYY')");
            oracleSql = oracleSql.replace(/strftime\('%Y-%m', ([^)]+)\)/g, "TO_CHAR($1, 'YYYY-MM')");

            const result = await connection.execute(oracleSql, params);

            if (callback) {
                callback(null, result.rows || []);
            }
        } catch (err) {
            console.error('Error in db.all:', err);
            console.error('SQL:', sql);
            console.error('Params:', params);
            if (callback) callback(err, []);
        } finally {
            if (connection) {
                try {
                    await connection.close();
                } catch (err) {
                    console.error('Error closing connection:', err);
                }
            }
        }
    },

    // db.close()
    close: async function () {
        if (pool) {
            await pool.close();
            console.log('Oracle connection pool closed');
        }
    }
};

// Inicializar el pool al cargar el módulo
initialize().catch(err => {
    console.error('Failed to initialize Oracle connection pool:', err);
    process.exit(1);
});

module.exports = db;
