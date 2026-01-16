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
    role TEXT NOT NULL DEFAULT 'tutor_analista',
    branch_id INTEGER,
    supervisor_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (supervisor_id) REFERENCES users(id)
);

-- Employees Table
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    branch_id INTEGER,
    hire_date DATE,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- Incidents Table
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_id INTEGER NOT NULL,
    reported_by INTEGER NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    start_date DATE,
    end_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (reported_by) REFERENCES users(id)
);

-- Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_id INTEGER, 
    user_id INTEGER,
    month INTEGER,
    year INTEGER,
    data TEXT, -- JSON string
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status TEXT, -- 'present', 'absent', 'vacation', 'permission', 'incapacity'
    comment TEXT,
    arrival_time TEXT,
    permission_type TEXT,
    start_date DATE,
    end_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Attendance Roster
CREATE TABLE IF NOT EXISTS attendance_roster (
    employee_id INTEGER PRIMARY KEY,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
`;

const seedData = `
-- Seed Branches
INSERT OR IGNORE INTO branches (id, name, location) VALUES 
(1, 'Corporativo', 'CDMX'),
(2, 'Sucursal Norte', 'Monterrey'),
(3, 'Sucursal Sur', 'Guadalajara');
`;

console.log('Initializing SQLite Database...');

db.serialize(() => {
    // Enable Foreign Keys
    db.run("PRAGMA foreign_keys = ON");

    // Execute Schema
    db.exec(schema, (err) => {
        if (err) {
            console.error('Error creating schema:', err);
            return;
        }
        console.log('Tables created successfully.');

        // Execute Seed Data
        db.exec(seedData, (err) => {
            if (err) {
                console.error('Error seeding data:', err);
                return;
            }
            console.log('Initial seed data inserted.');
        });
    });
});
