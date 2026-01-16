const db = require('./database');

const schema = `
-- Branches Table
CREATE TABLE IF NOT EXISTS branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT
);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'tutor_analista', 'gerente', 'rrhh', 'soporte')),
    branch_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- Employees Table
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    branch_id INTEGER,
    hire_date DATE,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'vacation', 'sick_leave')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- Incidents Table
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_id INTEGER NOT NULL,
    reported_by INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('luz', 'internet', 'equipo', 'correo', 'otro')),
    description TEXT,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (reported_by) REFERENCES users(id)
);

-- Reports Table
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    report_date DATE NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
`;

const seedData = `
-- Seed Branches
INSERT OR IGNORE INTO branches (id, name, location) VALUES 
(1, 'Corporativo', 'CDMX'),
(2, 'Sucursal Norte', 'Monterrey'),
(3, 'Sucursal Sur', 'Guadalajara');

-- Seed Admin User
INSERT OR IGNORE INTO users (username, password_hash, role, branch_id) VALUES 
('admin', 'admin123', 'admin', 1);
`;

db.serialize(() => {
    db.exec(schema, (err) => {
        if (err) {
            console.error('Error creating schema:', err);
        } else {
            console.log('Tables created successfully.');

            db.exec(seedData, (err) => {
                if (err) {
                    console.error('Error seeding data:', err);
                } else {
                    console.log('Seed data inserted.');
                }
            });
        }
    });
});
