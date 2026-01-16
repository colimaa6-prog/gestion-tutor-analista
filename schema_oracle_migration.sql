-- =====================================================================
-- SCHEMA ORACLE - MIGRACIÓN COMPLETA DE SQLITE
-- =====================================================================
-- Este script crea todas las tablas necesarias en Oracle Autonomous Database
-- Compatible con Oracle 19c+
-- =====================================================================

-- Limpiar tablas existentes (si existen)
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE reports CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE attendance CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE attendance_roster CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE incidents CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE employees CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE branches CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE users CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- =====================================================================
-- TABLA: users
-- =====================================================================
CREATE TABLE users (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR2(100) UNIQUE NOT NULL,
    password_hash VARCHAR2(255) NOT NULL,
    role VARCHAR2(50) DEFAULT 'tutor_analista',
    supervisor_id NUMBER,
    branch_id NUMBER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_supervisor FOREIGN KEY (supervisor_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_users_supervisor ON users(supervisor_id);
CREATE INDEX idx_users_role ON users(role);

-- =====================================================================
-- TABLA: branches
-- =====================================================================
CREATE TABLE branches (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR2(200) NOT NULL,
    location VARCHAR2(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- TABLA: employees
-- =====================================================================
CREATE TABLE employees (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR2(200) NOT NULL,
    branch_id NUMBER,
    hire_date DATE,
    status VARCHAR2(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_employees_branch FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

CREATE INDEX idx_employees_branch ON employees(branch_id);
CREATE INDEX idx_employees_status ON employees(status);

-- =====================================================================
-- TABLA: incidents
-- =====================================================================
CREATE TABLE incidents (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id NUMBER,
    reported_by NUMBER NOT NULL,
    type VARCHAR2(100) NOT NULL,
    status VARCHAR2(50) DEFAULT 'pending',
    description CLOB,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_incidents_branch FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
    CONSTRAINT fk_incidents_reporter FOREIGN KEY (reported_by) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE INDEX idx_incidents_branch ON incidents(branch_id);
CREATE INDEX idx_incidents_reporter ON incidents(reported_by);
CREATE INDEX idx_incidents_status ON incidents(status);

-- =====================================================================
-- TABLA: attendance_roster
-- =====================================================================
CREATE TABLE attendance_roster (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id NUMBER NOT NULL,
    added_by_user_id NUMBER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_roster_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    CONSTRAINT fk_roster_user FOREIGN KEY (added_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT uk_roster_employee UNIQUE (employee_id)
);

CREATE INDEX idx_roster_added_by ON attendance_roster(added_by_user_id);

-- =====================================================================
-- TABLA: attendance
-- =====================================================================
CREATE TABLE attendance (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id NUMBER NOT NULL,
    date DATE NOT NULL,
    status VARCHAR2(50) NOT NULL,
    comment VARCHAR2(500),
    arrival_time VARCHAR2(10),
    permission_type VARCHAR2(100),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    CONSTRAINT uk_attendance_emp_date UNIQUE (employee_id, date)
);

CREATE INDEX idx_attendance_employee ON attendance(employee_id);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_status ON attendance(status);

-- =====================================================================
-- TABLA: reports
-- =====================================================================
CREATE TABLE reports (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id NUMBER NOT NULL,
    month NUMBER NOT NULL,
    year NUMBER NOT NULL,
    data CLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reports_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    CONSTRAINT uk_reports_emp_month UNIQUE (employee_id, month, year)
);

CREATE INDEX idx_reports_employee ON reports(employee_id);
CREATE INDEX idx_reports_month_year ON reports(month, year);

-- =====================================================================
-- DATOS INICIALES
-- =====================================================================

-- Insertar sucursales
INSERT INTO branches (name, location) VALUES ('Sucursal Centro', 'Centro');
INSERT INTO branches (name, location) VALUES ('Sucursal Norte', 'Zona Norte');
INSERT INTO branches (name, location) VALUES ('Sucursal Sur', 'Zona Sur');

COMMIT;

PROMPT
PROMPT ========================================
PROMPT ✅ Schema creado exitosamente
PROMPT ========================================
PROMPT Tablas creadas:
PROMPT - users
PROMPT - branches (3 registros)
PROMPT - employees
PROMPT - incidents
PROMPT - attendance_roster
PROMPT - attendance
PROMPT - reports
PROMPT ========================================
