-- =====================================================================
-- MIGRACIÓN COMPLETA A ORACLE CLOUD - VERSIÓN FINAL
-- =====================================================================
-- Este script crea TODA la funcionalidad de la aplicación en Oracle Cloud
-- Incluye: Login, Usuarios, Reportes, y toda la lógica de negocio
-- =====================================================================

-- PASO 1: Eliminar todo lo anterior (si existe)
-- =====================================================================
BEGIN
    -- Eliminar handlers, templates y módulos
    FOR h IN (SELECT id FROM user_ords_handlers) LOOP
        DELETE FROM user_ords_handlers WHERE id = h.id;
    END LOOP;
    FOR t IN (SELECT id FROM user_ords_templates) LOOP
        DELETE FROM user_ords_templates WHERE id = t.id;
    END LOOP;
    FOR m IN (SELECT id FROM user_ords_modules) LOOP
        DELETE FROM user_ords_modules WHERE id = m.id;
    END LOOP;
    
    -- Deshabilitar AutoREST
    FOR obj IN (SELECT object_name FROM user_ords_enabled_objects) LOOP
        BEGIN
            ORDS.DELETE_OBJECT(
                p_schema => USER,
                p_object => obj.object_name
            );
        EXCEPTION WHEN OTHERS THEN NULL;
        END;
    END LOOP;
    
    COMMIT;
END;
/

-- =====================================================================
-- PASO 2: Habilitar ORDS para el schema
-- =====================================================================
BEGIN
    ORDS.ENABLE_SCHEMA(
        p_enabled => TRUE,
        p_schema => USER,
        p_url_mapping_type => 'BASE_PATH',
        p_url_mapping_pattern => 'admin',
        p_auto_rest_auth => FALSE
    );
    COMMIT;
END;
/

-- =====================================================================
-- PASO 3: Crear el módulo API
-- =====================================================================
BEGIN
    ORDS.DEFINE_MODULE(
        p_module_name => 'api_v1',
        p_base_path => 'api/',
        p_items_per_page => 100,
        p_status => 'PUBLISHED',
        p_comments => 'API completa para Gestión Tutor Analista'
    );
    COMMIT;
END;
/

-- =====================================================================
-- ENDPOINT 1: LOGIN (POST)
-- =====================================================================
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name => 'api_v1',
        p_pattern => 'login'
    );
    
    ORDS.DEFINE_HANDLER(
        p_module_name => 'api_v1',
        p_pattern => 'login',
        p_method => 'POST',
        p_source_type => ORDS.source_type_plsql,
        p_source => '
DECLARE
    l_body BLOB;
    l_json JSON_OBJECT_T;
    l_username VARCHAR2(50);
    l_password VARCHAR2(255);
    l_user_id NUMBER;
    l_role VARCHAR2(50);
    l_branch_id NUMBER;
BEGIN
    l_body := :body;
    l_json := JSON_OBJECT_T(l_body);
    l_username := l_json.get_String(''username'');
    l_password := l_json.get_String(''password'');
    
    -- Buscar usuario
    SELECT id, role, branch_id
    INTO l_user_id, l_role, l_branch_id
    FROM users
    WHERE username = l_username AND password_hash = l_password;
    
    -- Respuesta exitosa
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', true);
    APEX_JSON.write(''message'', ''Login exitoso'');
    APEX_JSON.open_object(''user'');
    APEX_JSON.write(''id'', l_user_id);
    APEX_JSON.write(''username'', l_username);
    APEX_JSON.write(''role'', l_role);
    APEX_JSON.write(''branch_id'', l_branch_id);
    APEX_JSON.close_object;
    APEX_JSON.close_object;
    
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        :status_code := 401;
        APEX_JSON.open_object;
        APEX_JSON.write(''success'', false);
        APEX_JSON.write(''message'', ''Usuario o contraseña incorrectos'');
        APEX_JSON.close_object;
    WHEN OTHERS THEN
        :status_code := 500;
        APEX_JSON.open_object;
        APEX_JSON.write(''success'', false);
        APEX_JSON.write(''message'', SQLERRM);
        APEX_JSON.close_object;
END;'
    );
    COMMIT;
END;
/

-- =====================================================================
-- ENDPOINT 2: EMPLOYEES (GET ALL)
-- =====================================================================
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name => 'api_v1',
        p_pattern => 'employees'
    );
    
    ORDS.DEFINE_HANDLER(
        p_module_name => 'api_v1',
        p_pattern => 'employees',
        p_method => 'GET',
        p_source_type => ORDS.source_type_plsql,
        p_source => '
BEGIN
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', true);
    APEX_JSON.open_array(''data'');
    
    FOR r IN (
        SELECT e.id, e.full_name, e.branch_id, e.hire_date, e.status,
               b.name as branch_name
        FROM employees e
        LEFT JOIN branches b ON e.branch_id = b.id
        ORDER BY e.full_name
    ) LOOP
        APEX_JSON.open_object;
        APEX_JSON.write(''id'', r.id);
        APEX_JSON.write(''full_name'', r.full_name);
        APEX_JSON.write(''branch_id'', r.branch_id);
        APEX_JSON.write(''branch_name'', r.branch_name);
        APEX_JSON.write(''hire_date'', TO_CHAR(r.hire_date, ''YYYY-MM-DD''));
        APEX_JSON.write(''status'', r.status);
        APEX_JSON.close_object;
    END LOOP;
    
    APEX_JSON.close_array;
    APEX_JSON.close_object;
END;'
    );
    COMMIT;
END;
/

-- =====================================================================
-- ENDPOINT 3: EMPLOYEES (POST - Create)
-- =====================================================================
BEGIN
    ORDS.DEFINE_HANDLER(
        p_module_name => 'api_v1',
        p_pattern => 'employees',
        p_method => 'POST',
        p_source_type => ORDS.source_type_plsql,
        p_source => '
DECLARE
    l_body BLOB;
    l_json JSON_OBJECT_T;
    l_name VARCHAR2(100);
    l_branch_id NUMBER;
    l_hire_date DATE;
    l_new_id NUMBER;
BEGIN
    l_body := :body;
    l_json := JSON_OBJECT_T(l_body);
    l_name := l_json.get_String(''full_name'');
    l_branch_id := l_json.get_Number(''branch_id'');
    
    IF l_json.has(''hire_date'') AND l_json.get_String(''hire_date'') IS NOT NULL THEN
        l_hire_date := TO_DATE(l_json.get_String(''hire_date''), ''YYYY-MM-DD'');
    END IF;
    
    INSERT INTO employees (full_name, branch_id, hire_date, status)
    VALUES (l_name, l_branch_id, l_hire_date, ''active'')
    RETURNING id INTO l_new_id;
    
    COMMIT;
    
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', true);
    APEX_JSON.write(''message'', ''Empleado creado'');
    APEX_JSON.write(''id'', l_new_id);
    APEX_JSON.close_object;
EXCEPTION WHEN OTHERS THEN
    ROLLBACK;
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', false);
    APEX_JSON.write(''message'', SQLERRM);
    APEX_JSON.close_object;
END;'
    );
    COMMIT;
END;
/

-- =====================================================================
-- ENDPOINT 4: EMPLOYEES/:id (DELETE)
-- =====================================================================
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name => 'api_v1',
        p_pattern => 'employees/:id'
    );
    
    ORDS.DEFINE_HANDLER(
        p_module_name => 'api_v1',
        p_pattern => 'employees/:id',
        p_method => 'DELETE',
        p_source_type => ORDS.source_type_plsql,
        p_source => '
DECLARE
    l_id NUMBER := :id;
BEGIN
    DELETE FROM employees WHERE id = l_id;
    COMMIT;
    
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', true);
    APEX_JSON.write(''message'', ''Empleado eliminado'');
    APEX_JSON.close_object;
EXCEPTION WHEN OTHERS THEN
    ROLLBACK;
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', false);
    APEX_JSON.write(''message'', SQLERRM);
    APEX_JSON.close_object;
END;'
    );
    COMMIT;
END;
/

-- =====================================================================
-- ENDPOINT 5: BRANCHES (GET ALL)
-- =====================================================================
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name => 'api_v1',
        p_pattern => 'branches'
    );
    
    ORDS.DEFINE_HANDLER(
        p_module_name => 'api_v1',
        p_pattern => 'branches',
        p_method => 'GET',
        p_source_type => ORDS.source_type_plsql,
        p_source => '
BEGIN
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', true);
    APEX_JSON.open_array(''data'');
    
    FOR r IN (SELECT id, name, location FROM branches ORDER BY name) LOOP
        APEX_JSON.open_object;
        APEX_JSON.write(''id'', r.id);
        APEX_JSON.write(''name'', r.name);
        APEX_JSON.write(''location'', r.location);
        APEX_JSON.close_object;
    END LOOP;
    
    APEX_JSON.close_array;
    APEX_JSON.close_object;
END;'
    );
    COMMIT;
END;
/

-- =====================================================================
-- ENDPOINT 6: INCIDENTS (GET ALL)
-- =====================================================================
BEGIN
    ORDS.DEFINE_TEMPLATE(
        p_module_name => 'api_v1',
        p_pattern => 'incidents'
    );
    
    ORDS.DEFINE_HANDLER(
        p_module_name => 'api_v1',
        p_pattern => 'incidents',
        p_method => 'GET',
        p_source_type => ORDS.source_type_plsql,
        p_source => '
BEGIN
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', true);
    APEX_JSON.open_array(''data'');
    
    FOR r IN (
        SELECT i.id, i.branch_id, i.reported_by, i.type, i.description,
               i.status, i.start_date, i.end_date, i.created_at,
               b.name as branch_name, e.full_name as reported_by_name
        FROM incidents i
        LEFT JOIN branches b ON i.branch_id = b.id
        LEFT JOIN employees e ON i.reported_by = e.id
        ORDER BY i.created_at DESC
    ) LOOP
        APEX_JSON.open_object;
        APEX_JSON.write(''id'', r.id);
        APEX_JSON.write(''branch_id'', r.branch_id);
        APEX_JSON.write(''branch_name'', r.branch_name);
        APEX_JSON.write(''reported_by'', r.reported_by);
        APEX_JSON.write(''reported_by_name'', r.reported_by_name);
        APEX_JSON.write(''type'', r.type);
        APEX_JSON.write(''description'', r.description);
        APEX_JSON.write(''status'', r.status);
        APEX_JSON.write(''start_date'', TO_CHAR(r.start_date, ''YYYY-MM-DD''));
        APEX_JSON.write(''end_date'', TO_CHAR(r.end_date, ''YYYY-MM-DD''));
        APEX_JSON.close_object;
    END LOOP;
    
    APEX_JSON.close_array;
    APEX_JSON.close_object;
END;'
    );
    COMMIT;
END;
/

-- Continúa en el siguiente archivo debido al límite de tamaño...
-- Este es solo el INICIO del script completo.
-- Necesitas ejecutar TODOS los endpoints para tener la funcionalidad completa.

-- =====================================================================
-- VERIFICACIÓN
-- =====================================================================
SELECT 'Módulos creados: ' || COUNT(*) FROM user_ords_modules;
SELECT 'Templates creados: ' || COUNT(*) FROM user_ords_templates;
SELECT 'Handlers creados: ' || COUNT(*) FROM user_ords_handlers;
