@echo off
chcp 65001 > nul
cls
echo =======================================================
echo   TRANFERENCIA DE DATOS: RAILWAY (Origen) -> NEON (Destino)
echo =======================================================
echo.
echo Este script copiara los datos de tu base de datos actual en Railway
echo hacia la nueva base de datos en Neon.
echo.
echo Requisitos:
echo 1. DATABASE_URL en .env debe ser la de Railway (Ya configurado).
echo 2. Debes tener a mano la URL de conexion de Neon.
echo.

python migrate_railway_to_neon.py
pause
