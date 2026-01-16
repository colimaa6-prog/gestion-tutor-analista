-- =============================================================================
-- SCRIPT DE CREACIÓN DE USUARIO PARA GESTIÓN TUTOR ANALISTA
-- =============================================================================
-- Ejecuta este script como usuario ADMIN en Oracle Cloud Database Actions.
-- Este paso es NECESARIO para evitar errores de permisos (HTML response error).
-- =============================================================================

-- 1. Crear el usuario dedicado
-- Nota: Si el usuario ya existe, esta línea dará error, puedes ignorarlo o borrar el usuario antes
DECLARE
    user_exists NUMBER;
BEGIN
    SELECT count(*) INTO user_exists FROM dba_users WHERE username = 'GESTION_USER';
    IF user_exists = 0 THEN
        EXECUTE IMMEDIATE 'CREATE USER GESTION_USER IDENTIFIED BY "Gestion2025_App"';
    END IF;
END;
/

-- 2. Asignar permisos básicos
GRANT CONNECT, RESOURCE TO GESTION_USER;
GRANT UNLIMITED TABLESPACE TO GESTION_USER;

-- 3. Habilitar permisos para Servicios REST (ORDS)
GRANT DWROLE TO GESTION_USER;

-- 4. Activar ORDS para este esquema con el alias correcto
BEGIN
    ORDS.ENABLE_SCHEMA(
        p_enabled             => TRUE,
        p_schema              => 'GESTION_USER',
        p_url_mapping_type    => 'BASE_PATH',
        p_url_mapping_pattern => 'gestion_app', -- ALIAS IMPORTANTE: Debe coincidir con config.js
        p_auto_rest_auth      => FALSE
    );
    COMMIT;
END;
/

-- =============================================================================
-- INSTRUCCIONES SIGUIENTES:
-- 1. Cierra sesión del usuario ADMIN.
-- 2. Inicia sesión con:
--    Usuario: GESTION_USER
--    Contraseña: Gestion2025_App
-- 3. Abre el archivo "setup_ords.sql" y ejecútalo ENTERO en la nueva sesión.
-- =============================================================================
