-- =============================================================================
-- SCRIPT DE VERIFICACIÓN DE URLS (Ejecutar como ADMIN)
-- =============================================================================
-- Este script lista todas las URLs activas para que sepas cuál usar.
-- =============================================================================

SELECT 
    owner as ESQUEMA_DB, 
    pattern as URL_ALIAS, 
    type as TIPO_MAPPING,
    status as ESTADO
FROM all_ords_url_mappings
WHERE owner IN ('ADMIN', 'GESTION_USER')
ORDER BY owner;

-- INSTRUCCIONES:
-- 1. Ejecuta esto con el usuario ADMIN.
-- 2. Busca la fila que diga "GESTION_USER" en la columna ESQUEMA_DB.
-- 3. Mira qué dice la columna URL_ALIAS.
--    - Si dice "gestion_app", tu URL es .../ords/gestion_app/api
--    - Si dice otra cosa, ESA es la que debes poner en config.js
--    - Si NO aparece ninguna fila para GESTION_USER, es que no se ejecutó el ENABLE_SCHEMA.
