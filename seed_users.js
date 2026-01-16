const db = require('./database');

console.log('Starting user seeding...');

const admins = [
    { username: 'HELDER MORA', password_hash: 'Hmora', role: 'admin' },
    { username: 'ESTHFANIA RAMOS', password_hash: 'Eramos', role: 'admin' }
];

const teamHelder = [
    { username: 'ALFARO MARTINEZ KAREM JANETH', password_hash: 'Exitus.tap' },
    { username: 'RODRIGUEZ SALAZAR ANA CARLOTA', password_hash: 'Exitus.rod' },
    { username: 'MONTOYA GARCIA CHRISTINE', password_hash: 'Exitus.san' },
    { username: 'JIMENEZ HEREDIA JESSICA', password_hash: 'Exitus.car' },
    { username: 'TORRES MEDINA MARIA ANTONIA', password_hash: 'Exitus.tam' },
    { username: 'DE LA CRUZ JUAREZ KARLA MARINA', password_hash: 'Exitus.apo' }
];

const teamEsthfania = [
    { username: 'FIERRO GALEANA ASAN ZZU', password_hash: 'Exitus.cua' },
    { username: 'REYES CANO DULCE MARLEN', password_hash: 'Exitus.ajh' },
    { username: 'BAEZ NIEVES SANDRA RUTH', password_hash: 'Exitus.ayo' },
    { username: 'MORALES HERNANDEZ ROSALIA', password_hash: 'Exitus.chi' },
    { username: 'GONZALEZ LOPEZ MARIA ISABEL', password_hash: 'Exitus.ixt' },
    { username: 'MARTINEZ ZABALETA MARIELA SOLEDAD', password_hash: 'Exitus.ver' }
];

async function upsertUser(user, defaultBranchId, supervisorId) {
    const role = user.role || 'tutor_analista';
    const cleanBranchId = user.branch_id || defaultBranchId;

    return new Promise((resolve, reject) => {
        // Try UPDATE first
        db.run(
            "UPDATE users SET password_hash = ?, role = ?, supervisor_id = ?, branch_id = ? WHERE username = ?",
            [user.password_hash, role, supervisorId, cleanBranchId, user.username],
            function (err) {
                if (err) {
                    console.error(`Error updating ${user.username}:`, err.message);
                    return resolve(); // Don't stop all seeding
                }

                if (this.changes > 0) {
                    console.log(`✓ Updated user ${user.username}`);
                    resolve();
                } else {
                    // User did not exist, INSERT
                    db.run(
                        "INSERT INTO users (username, password_hash, role, supervisor_id, branch_id) VALUES (?, ?, ?, ?, ?)",
                        [user.username, user.password_hash, role, supervisorId, cleanBranchId],
                        function (err) {
                            if (err) console.error(`Error inserting ${user.username}:`, err.message);
                            else console.log(`✓ Created user ${user.username}`);
                            resolve();
                        }
                    );
                }
            }
        );
    });
}

async function getUserId(username) {
    return new Promise((resolve, reject) => {
        db.get("SELECT id FROM users WHERE username = ?", [username], (err, row) => {
            if (err || !row) resolve(null);
            else resolve(row.id);
        });
    });
}

(async () => {
    // We cannot use db.serialize() because it's SQLite-specific and not in our adapter.
    // We use async/await instead.

    // 1. Handle Admin 1: HELDER MORA
    await upsertUser(admins[0], 1, null);
    const admin1Id = await getUserId(admins[0].username);

    if (admin1Id) {
        for (const user of teamHelder) {
            await upsertUser(user, 1, admin1Id);
        }
    } else {
        console.error("Could not find ID for Admin 1");
    }

    // 2. Handle Admin 2: ESTHFANIA RAMOS
    await upsertUser(admins[1], 1, null);
    const admin2Id = await getUserId(admins[1].username);

    if (admin2Id) {
        for (const user of teamEsthfania) {
            await upsertUser(user, 1, admin2Id);
        }
    } else {
        console.error("Could not find ID for Admin 2");
    }

    console.log("Seeding complete.");
})();
