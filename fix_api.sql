-- =============================================================================
-- SCRIPT DE REPARACIÓN DE LA API (ORDS MODULE)
-- =============================================================================
-- Ejecuta este script conectado como: GESTION_USER
-- =============================================================================

BEGIN
    -- 1. Eliminar el módulo anterior para asegurar limpieza
    ORDS.DELETE_MODULE(
        p_module_name => 'api'
    );
    
    -- 2. Volver a definir el módulo
    ORDS.DEFINE_MODULE(
        p_module_name    => 'api',
        p_base_path      => 'api/',  -- Esto se suma al alias del esquema
        p_items_per_page => 25,
        p_status         => 'PUBLISHED',
        p_comments       => 'API Gestion Tutor - Recreada'
    );

    -- 3. Definir Endpoint: LOGIN (Prueba principal)
    ORDS.DEFINE_TEMPLATE(
        p_module_name    => 'api',
        p_pattern        => 'login'
    );

    ORDS.DEFINE_HANDLER(
        p_module_name    => 'api',
        p_pattern        => 'login',
        p_method         => 'POST',
        p_source_type    => ORDS.source_type_plsql,
        p_source         => '
DECLARE
    l_body    BLOB;
    l_json    JSON_OBJECT_T;
    l_user    VARCHAR2(50);
    l_pass    VARCHAR2(50);
    l_id      NUMBER;
    l_role    VARCHAR2(50);
    l_branch  NUMBER;
BEGIN
    l_body := :body;
    
    -- Manejo básico de error si el body está vacío
    IF l_body IS NULL THEN
        :status_code := 400;
        APEX_JSON.open_object;
        APEX_JSON.write(''success'', false);
        APEX_JSON.write(''message'', ''Cuerpo de petición vacío'');
        APEX_JSON.close_object;
        RETURN;
    END IF;

    l_json := JSON_OBJECT_T(l_body);
    l_user := l_json.get_String(''username'');
    l_pass := l_json.get_String(''password'');
    
    SELECT id, role, branch_id 
    INTO l_id, l_role, l_branch
    FROM users 
    WHERE username = l_user AND password_hash = l_pass;
    
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', true);
    APEX_JSON.write(''message'', ''Bienvenido'');
    APEX_JSON.open_object(''user'');
    APEX_JSON.write(''id'', l_id);
    APEX_JSON.write(''username'', l_user);
    APEX_JSON.write(''role'', l_role);
    APEX_JSON.write(''branch_id'', l_branch);
    APEX_JSON.close_object;
    APEX_JSON.close_object;
EXCEPTION WHEN NO_DATA_FOUND THEN
    :status_code := 401;
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', false);
    APEX_JSON.write(''message'', ''Usuario o contraseña incorrectos'');
    APEX_JSON.close_object;
WHEN OTHERS THEN
    :status_code := 500;
    APEX_JSON.open_object;
    APEX_JSON.write(''success'', false);
    APEX_JSON.write(''message'', ''Error interno: '' || SQLERRM);
    APEX_JSON.close_object;
END;'
    );
    
    COMMIT;
END;
/

-- Imprimir confirmación
SELECT 'API Re-creada exitosamente.' as status FROM dual;
