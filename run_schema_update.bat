@echo off
SET "NODE_PATH=C:\APP\node-v24.12.0-win-x64\node-v24.12.0-win-x64"
SET "PATH=%NODE_PATH%;%PATH%"

echo ========================================
echo   Actualizando esquema de usuarios
echo ========================================
echo.
node update_users_schema.js
echo.
pause
