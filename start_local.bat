@echo off
echo ===================================================
echo INICIANDO SERVIDOR LOCAL (MODO JSON/SQLITE)
echo ===================================================
echo.

set NODE_PATH="C:\APP\node-v24.12.0-win-x64\node.exe"
set NPM_PATH="C:\APP\node-v24.12.0-win-x64\npm.cmd"

echo Usando Node en: %NODE_PATH%

REM Instalar dependencias si faltan
if not exist "node_modules" (
    echo [INFO] Instalando dependencias necesarias...
    call %NPM_PATH% install
)

REM Inicializar base de datos si no existe (o si se quiere resetear)
if not exist "gestion_tutor.db" (
    echo [INFO] Base de datos no encontrada. Inicializando...
    %NODE_PATH% init_db_complete.js
    %NODE_PATH% seed_users.js
)

echo.
echo [INFO] Iniciando aplicacion...
echo Abre tu navegador en: http://localhost:3000
echo.

%NODE_PATH% server.js
pause
