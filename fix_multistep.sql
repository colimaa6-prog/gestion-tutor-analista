-- =============================================================================
-- SCRIPT DE MAPPING DE URL (FIX DEFINITIVO 404)
-- =============================================================================
-- Ejecuta este script conectado como: GESTION_USER
-- Este script asegura que la URL ".../ords/gestion_app/..." esté activa.
-- =============================================================================

BEGIN
    -- 1. Habilitar el esquema explícitamente con el alias correcto
    ORDS.ENABLE_SCHEMA(
        p_enabled             => TRUE,
        p_schema              => 'GESTION_USER',
        p_url_mapping_type    => 'BASE_PATH',
        p_url_mapping_pattern => 'gestion_app', -- Este es el ALIAS CLAVE
        p_auto_rest_auth      => FALSE          -- FALSE permite acceso público sin OAuth
    );
    
    -- 2. Asegurar que los cambios se guarden
    COMMIT;
END;
/

-- 3. Verificación (Solo informativo)
-- Si esto devuelve una fila, el alias está activo.
SELECT * 
FROM user_ords_schemas 
WHERE url_mapping_pattern = 'gestion_app';
