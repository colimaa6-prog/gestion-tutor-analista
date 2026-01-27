@echo off
chcp 65001 > nul
cls
echo ==================================================
echo      MIGRACIÓN A BASE DE DATOS NEON (POSTGRES)
echo ==================================================
echo.
echo Este script migrará tus tablas y datos de SQLite (local) a Neon.
echo Asegúrate de tener tu DATABASE_URL de Neon a mano.
echo.

if not exist .env (
    echo El archivo .env no existe. Crealo o introduce la URL manualmente.
)

python migrate_to_postgres_v2.py
pause
