-- =============================================================================
-- SCRIPT DE CREACIÓN FORZADA DE USUARIO (SOLUCIÓN FINAL ERROR ORA-01918)
-- =============================================================================
-- Ejecuta este script conectado como: ADMIN
-- Este script BORRARÁ al usuario si existe a medias y lo creará de nuevo limpio.
-- =============================================================================

BEGIN
    -- 1. Intentar borrar el usuario si existe (para limpiar errores previos)
    BEGIN
        EXECUTE IMMEDIATE 'DROP USER GESTION_USER CASCADE';
    EXCEPTION WHEN OTHERS THEN NULL; -- Ignorar si no existe
    END;

    -- 2. Crear el usuario desde cero
    EXECUTE IMMEDIATE 'CREATE USER GESTION_USER IDENTIFIED BY "Gestion2025_App"';

    -- 3. Dar permisos vitales
    EXECUTE IMMEDIATE 'GRANT CONNECT, RESOURCE TO GESTION_USER';
    EXECUTE IMMEDIATE 'GRANT UNLIMITED TABLESPACE TO GESTION_USER';
    -- Permiso DWROLE es necesario en Autonomous Database para usar herramientas Web
    EXECUTE IMMEDIATE 'GRANT DWROLE TO GESTION_USER';

    -- 4. Habilitar ORDS para este usuario (para que tenga URL propia)
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
