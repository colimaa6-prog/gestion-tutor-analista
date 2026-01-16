-- =============================================================================
-- SCRIPT DE MAPPING DE URL (VERSIÓN CORREGIDA)
-- =============================================================================
-- Ejecuta este script conectado como: GESTION_USER
-- =============================================================================

BEGIN
    -- Habilitar esquema con el alias 'gestion_app'
    ORDS.ENABLE_SCHEMA(
        p_enabled             => TRUE,
        p_schema              => 'GESTION_USER',
        p_url_mapping_type    => 'BASE_PATH',
        p_url_mapping_pattern => 'gestion_app',
        p_auto_rest_auth      => FALSE
    );
    COMMIT;
END;
/

-- Si este script termina con "PL/SQL procedure successfully completed",
-- entonces el alias ya está activo.
