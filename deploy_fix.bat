@echo off
chcp 65001 > nul
cls
echo =======================================================
echo      SUBIENDO CAMBIOS A GITHUB PARA RENDER (FIX)
echo =======================================================
echo.
echo 1. Agregando runtime.txt para forzar Python 3.11...
git add .

echo 2. Creando commit...
git commit -m "Fix: Force Python 3.11 in Render via runtime.txt"

echo 3. Subiendo a GitHub...
git push

echo.
echo =======================================================
echo ¡Listo! Render debería detectar el cambio, usar Python 3.11 y compilar correctamente.
echo =======================================================
pause
