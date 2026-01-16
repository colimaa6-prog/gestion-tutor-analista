@echo off
SET "NODE_PATH=C:\APP\node-v24.12.0-win-x64\node-v24.12.0-win-x64"
SET "PATH=%NODE_PATH%;%PATH%"

echo ==========================================
echo Reparando instalacion del sistema...
echo ==========================================

echo 1. Eliminando archivos corruptos...
if exist node_modules (
    rmdir /s /q node_modules
)
if exist package-lock.json (
    del package-lock.json
)

echo 2. Limpiando cache...
call npm.cmd cache clean --force

echo 3. Instalando dependencias (esto puede tardar unos minutos)...
call npm.cmd install

echo ==========================================
echo Reparacion completada.
echo Ahora intenta abrir de nuevo "start_server.bat"
echo ==========================================
pause
