-- Script para verificar datos migrados en PostgreSQL
-- Ejecutar este script en Railway para diagnosticar problemas

-- 1. Verificar cuántos empleados tienen fecha de ingreso
SELECT 
    COUNT(*) as total_empleados,
    COUNT(hire_date) as con_fecha_ingreso,
    COUNT(*) - COUNT(hire_date) as sin_fecha_ingreso
FROM employees;

-- 2. Mostrar algunos empleados sin fecha de ingreso (si existen)
SELECT id, full_name, hire_date, branch_id
FROM employees
WHERE hire_date IS NULL
LIMIT 10;

-- 3. Verificar el roster de asistencias
SELECT COUNT(*) as total_en_roster
FROM attendance_roster;

-- 4. Verificar usuarios
SELECT id, username, role, supervisor_id
FROM users
ORDER BY id;

-- 5. Verificar branches
SELECT * FROM branches ORDER BY id;
