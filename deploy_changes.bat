@echo off
chcp 65001 > nul
cls
echo =======================================================
echo      SUBIENDO CAMBIOS A GITHUB PARA RENDER
echo =======================================================
echo.
echo 1. Agregando archivos modificados (requirements.txt, Procfile, etc.)...
git add .

echo 2. Creando commit...
git commit -m "Preparar para despliegue en Render: agregar gunicorn y config de DB"

echo 3. Subiendo a GitHub...
git push

echo.
echo =======================================================
echo ¡Listo! Ahora ve a Render y verás que comienza un nuevo despliegue.
echo =======================================================
pause
