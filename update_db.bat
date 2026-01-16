@echo off
echo ========================================
echo  Actualizando Base de Datos
echo ========================================
echo.
echo Este script agregara nuevas columnas a la tabla de asistencias
echo para soportar comentarios y campos adicionales.
echo.
pause

"C:\APP\node-v24.12.0-win-x64\node-v24.12.0-win-x64\node.exe" update_attendance_schema.js

echo.
echo ========================================
echo  Proceso completado
echo ========================================
echo.
pause
