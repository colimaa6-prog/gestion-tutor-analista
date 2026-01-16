-- Script para inicializar PostgreSQL en Railway
-- Ejecutar este script en Railway después de crear la base de datos

-- Crear tablas
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'tutor_analista',
    supervisor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    branch_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    hire_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    reported_by INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance_roster (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    added_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    comment VARCHAR(500),
    arrival_time VARCHAR(10),
    permission_type VARCHAR(100),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, date)
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, month, year)
);

-- Crear índices
CREATE INDEX IF NOT EXISTS idx_users_supervisor ON users(supervisor_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_employees_branch ON employees(branch_id);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);
CREATE INDEX IF NOT EXISTS idx_incidents_branch ON incidents(branch_id);
CREATE INDEX IF NOT EXISTS idx_incidents_reporter ON incidents(reported_by);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_roster_added_by ON attendance_roster(added_by_user_id);
CREATE INDEX IF NOT EXISTS idx_attendance_employee ON attendance(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status);
CREATE INDEX IF NOT EXISTS idx_reports_employee ON reports(employee_id);
CREATE INDEX IF NOT EXISTS idx_reports_month_year ON reports(month, year);

-- Insertar datos iniciales
INSERT INTO branches (name, location) VALUES 
    ('Sucursal Centro', 'Centro'),
    ('Sucursal Norte', 'Zona Norte'),
    ('Sucursal Sur', 'Zona Sur')
ON CONFLICT DO NOTHING;

-- Insertar usuarios (administradores y tutores)
INSERT INTO users (username, password_hash, role, supervisor_id) VALUES
    ('HELDER MORA', 'Hmora', 'admin', NULL),
    ('ESTHFANIA RAMOS', 'Eramos', 'admin', NULL),
    ('JOSE LUIS ORTIZ', 'Jortiz', 'tutor_analista', 1),
    ('MARIA GONZALEZ', 'Mgonzalez', 'tutor_analista', 1),
    ('CARLOS RAMIREZ', 'Cramirez', 'tutor_analista', 1),
    ('ANA MARTINEZ', 'Amartinez', 'tutor_analista', 1),
    ('LUIS HERNANDEZ', 'Lhernandez', 'tutor_analista', 1),
    ('SOFIA LOPEZ', 'Slopez', 'tutor_analista', 1),
    ('MIGUEL GARCIA', 'Mgarcia', 'tutor_analista', 2),
    ('LAURA RODRIGUEZ', 'Lrodriguez', 'tutor_analista', 2),
    ('PEDRO SANCHEZ', 'Psanchez', 'tutor_analista', 2),
    ('CARMEN TORRES', 'Ctorres', 'tutor_analista', 2),
    ('JORGE FLORES', 'Jflores', 'tutor_analista', 2),
    ('ISABEL MORALES', 'Imorales', 'tutor_analista', 2)
ON CONFLICT (username) DO NOTHING;
