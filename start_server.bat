@echo off
SET "NODE_PATH=C:\APP\node-v24.12.0-win-x64"
SET "PATH=%NODE_PATH%;%PATH%"

echo Iniciando servidor...
node server.js
pause
