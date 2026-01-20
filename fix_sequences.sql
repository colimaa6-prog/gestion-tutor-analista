-- Script para arreglar las secuencias de PostgreSQL
-- Ejecutar este script si hay problemas con IDs duplicados

-- Arreglar secuencia de branches
SELECT setval('branches_id_seq', (SELECT COALESCE(MAX(id), 1) FROM branches));

-- Arreglar secuencia de employees
SELECT setval('employees_id_seq', (SELECT COALESCE(MAX(id), 1) FROM employees));

-- Arreglar secuencia de users (por si acaso)
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));

-- Arreglar secuencia de attendance
SELECT setval('attendance_id_seq', (SELECT COALESCE(MAX(id), 1) FROM attendance));

-- Arreglar secuencia de incidents
SELECT setval('incidents_id_seq', (SELECT COALESCE(MAX(id), 1) FROM incidents));

-- Arreglar secuencia de reports
SELECT setval('reports_id_seq', (SELECT COALESCE(MAX(id), 1) FROM reports));

-- Verificar que las secuencias estén correctas
SELECT 'branches_id_seq' as tabla, last_value FROM branches_id_seq
UNION ALL
SELECT 'employees_id_seq', last_value FROM employees_id_seq
UNION ALL
SELECT 'users_id_seq', last_value FROM users_id_seq
UNION ALL
SELECT 'attendance_id_seq', last_value FROM attendance_id_seq
UNION ALL
SELECT 'incidents_id_seq', last_value FROM incidents_id_seq
UNION ALL
SELECT 'reports_id_seq', last_value FROM reports_id_seq;
