-- =====================================================================
-- SCRIPT DE VERIFICACIÓN COMPLETA DE ORDS
-- =====================================================================
-- Ejecuta este script en Oracle Cloud SQL para diagnosticar el problema
-- =====================================================================

SET SERVEROUTPUT ON SIZE UNLIMITED;
SET LINESIZE 200;

PROMPT ===================================================================
PROMPT 1. VERIFICAR SCHEMA ORDS
PROMPT ===================================================================

SELECT 
    name as "Schema Name",
    url_mapping_pattern as "URL Pattern",
    CASE 
        WHEN url_mapping_pattern IS NOT NULL 
        THEN 'https://g6e58321a672730-rggestiontutor.adb.mx-queretaro-1.oraclecloudapps.com/ords/' || url_mapping_pattern || '/'
        ELSE 'NO CONFIGURADO'
    END as "Base URL"
FROM user_ords_schemas;

PROMPT
PROMPT ===================================================================
PROMPT 2. VERIFICAR MÓDULOS
PROMPT ===================================================================

SELECT 
    id,
    name as "Module Name",
    base_path as "Base Path",
    status as "Status"
FROM user_ords_modules;

PROMPT
PROMPT ===================================================================
PROMPT 3. VERIFICAR TEMPLATES (ENDPOINTS)
PROMPT ===================================================================

SELECT 
    t.id,
    m.name as "Module",
    t.uri_template as "Endpoint",
    COUNT(h.id) as "Handlers"
FROM user_ords_templates t
LEFT JOIN user_ords_modules m ON t.module_id = m.id
LEFT JOIN user_ords_handlers h ON t.id = h.template_id
GROUP BY t.id, m.name, t.uri_template
ORDER BY t.uri_template;

PROMPT
PROMPT ===================================================================
PROMPT 4. VERIFICAR HANDLERS (MÉTODOS HTTP)
PROMPT ===================================================================

SELECT 
    t.uri_template as "Endpoint",
    h.method as "HTTP Method",
    h.source_type as "Source Type"
FROM user_ords_templates t
JOIN user_ords_handlers h ON t.id = h.template_id
ORDER BY t.uri_template, h.method;

PROMPT
PROMPT ===================================================================
PROMPT 5. BUSCAR ENDPOINT DE INCIDENTS ESPECÍFICAMENTE
PROMPT ===================================================================

SELECT 
    m.name || '/' || m.base_path || t.uri_template as "Full Path",
    h.method as "Method"
FROM user_ords_templates t
JOIN user_ords_modules m ON t.module_id = m.id
JOIN user_ords_handlers h ON t.id = h.template_id
WHERE LOWER(t.uri_template) LIKE '%incident%'
ORDER BY h.method;

PROMPT
PROMPT ===================================================================
PROMPT 6. GENERAR URLs COMPLETAS PARA TODOS LOS ENDPOINTS
PROMPT ===================================================================

DECLARE
    v_base_url VARCHAR2(500) := 'https://g6e58321a672730-rggestiontutor.adb.mx-queretaro-1.oraclecloudapps.com/ords/';
    v_schema_pattern VARCHAR2(100);
BEGIN
    -- Obtener el patrón del schema
    SELECT url_mapping_pattern INTO v_schema_pattern 
    FROM user_ords_schemas 
    WHERE ROWNUM = 1;
    
    DBMS_OUTPUT.PUT_LINE('URLs COMPLETAS DE TODOS LOS ENDPOINTS:');
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('');
    
    FOR rec IN (
        SELECT DISTINCT
            m.base_path,
            t.uri_template,
            h.method
        FROM user_ords_templates t
        JOIN user_ords_modules m ON t.module_id = m.id
        JOIN user_ords_handlers h ON t.id = h.template_id
        ORDER BY t.uri_template, h.method
    ) LOOP
        DBMS_OUTPUT.PUT_LINE(
            rec.method || ' -> ' || 
            v_base_url || v_schema_pattern || '/' || rec.base_path || rec.uri_template
        );
    END LOOP;
    
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('========================================');
    DBMS_OUTPUT.PUT_LINE('URL BASE DEL API:');
    DBMS_OUTPUT.PUT_LINE(v_base_url || v_schema_pattern || '/api/v1/');
    
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: No se encontró configuración de schema ORDS');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
END;
/

PROMPT
PROMPT ===================================================================
PROMPT 7. VERIFICAR SI HAY ERRORES EN LOS HANDLERS
PROMPT ===================================================================

SELECT 
    t.uri_template,
    h.method,
    CASE 
        WHEN h.source IS NULL THEN 'ERROR: No hay código fuente'
        WHEN LENGTH(h.source) < 50 THEN 'WARNING: Código muy corto'
        ELSE 'OK'
    END as "Status"
FROM user_ords_templates t
JOIN user_ords_handlers h ON t.id = h.template_id
ORDER BY t.uri_template;

PROMPT
PROMPT ===================================================================
PROMPT DIAGNÓSTICO COMPLETADO
PROMPT ===================================================================
PROMPT
PROMPT Copia TODA la salida de este script y compártela para diagnosticar
PROMPT el problema.
PROMPT ===================================================================
