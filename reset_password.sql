-- =============================================================================
-- SCRIPT DE RESETEO DE CONTRASEÑA y ACTITVACIÓN DE USUARIO
-- =============================================================================
-- Ejecuta esto como usuario ADMIN para arreglar el acceso de GESTION_USER
-- =============================================================================

BEGIN
    -- 1. Resetear la contraseña (asegurando limpieza y sin caracteres extraños)
    EXECUTE IMMEDIATE 'ALTER USER GESTION_USER IDENTIFIED BY "Gestion2025_App"';
    
    -- 2. Desbloquear la cuenta por si acaso
    EXECUTE IMMEDIATE 'ALTER USER GESTION_USER ACCOUNT UNLOCK';
    
    -- 3. Habilitar el acceso a Database Actions (SQL Developer Web) para este usuario
    ORDS_ADMIN.ENABLE_SCHEMA(
        p_enabled             => TRUE,
        p_schema              => 'GESTION_USER',
        p_url_mapping_type    => 'BASE_PATH',
        p_url_mapping_pattern => 'gestion_app',
        p_auto_rest_auth      => FALSE -- Importante: FALSE para que tu App pueda entrar sin login complejo
    );
    
    COMMIT;
END;
/
