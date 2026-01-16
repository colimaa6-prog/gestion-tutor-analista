-- Database Creation
CREATE DATABASE IF NOT EXISTS gestion_tutor;
USE gestion_tutor;

-- Branches Table (Sucursales)
CREATE TABLE IF NOT EXISTS branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255)
);

-- Users Table (Usuarios)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'tutor_analista', 'gerente', 'rrhh', 'soporte') NOT NULL,
    branch_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- Employees Table (Empleados)
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    branch_id INT,
    hire_date DATE,
    status ENUM('active', 'inactive', 'vacation', 'sick_leave') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- Incidents Table (Incidencias)
CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    reported_by INT NOT NULL,
    type ENUM('luz', 'internet', 'equipo', 'correo', 'otro') NOT NULL,
    description TEXT,
    status ENUM('open', 'in_progress', 'resolved') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (reported_by) REFERENCES users(id)
);

-- Reports Table (Reportes de Gestión)
CREATE TABLE IF NOT EXISTS daily_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    user_id INT NOT NULL,
    report_date DATE NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- SEED DATA
INSERT INTO branches (name, location) VALUES 
('Corporativo', 'CDMX'),
('Sucursal Norte', 'Monterrey'),
('Sucursal Sur', 'Guadalajara');

-- Admin User (Password: admin123 - placeholder hash needed in real app)
-- In a real app, passwords must be hashed. This is for initial setup.
INSERT INTO users (username, password_hash, role, branch_id) VALUES 
('admin', 'admin123', 'admin', 1);
