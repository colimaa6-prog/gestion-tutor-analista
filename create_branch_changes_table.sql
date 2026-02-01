-- Tabla para registrar cambios en sucursales (rotación de personal)
CREATE TABLE IF NOT EXISTS branch_changes (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id),
    branch_name VARCHAR(200),
    change_type VARCHAR(20) NOT NULL, -- 'ingreso' o 'egreso'
    employee_name VARCHAR(200),
    hire_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    processed_by INTEGER REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_branch_changes_processed ON branch_changes(processed);
CREATE INDEX IF NOT EXISTS idx_branch_changes_created ON branch_changes(created_at);
