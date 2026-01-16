# Guía de Instalación y Ejecución - Gestión Tutor Analista

Actualmente, al abrir `index.html` solo ves la parte visual (Frontend). Para que el sistema funcione completamente (Login, Base de Datos, etc.), necesitas activar el "cerebro" del sistema (Backend).

Sigue estos pasos:

## 1. Instalar Node.js (El Motor)
El sistema necesita Node.js para funcionar.
1. Ve a [nodejs.org](https://nodejs.org/) y descarga la versión **LTS**.
2. Instálalo (siguiente, siguiente, siguiente...).
3. **Importante:** Cierra y vuelve a abrir tu terminal (PowerShell o CMD) para que se actualice.

## 2. Instalar Dependencias
Una vez tengas Node.js:
1. Abre una terminal en esta carpeta.
2. Escribe el siguiente comando y presiona Enter:
   ```bash
   npm install
   ```
   *Esto descargará las librerías necesarias (Express, MySQL, etc.).*

## 3. Configurar Base de Datos
Necesitas tener MySQL instalado (por ejemplo con XAMPP o MySQL Workbench).
1. Abre tu gestor de base de datos.
2. Ejecuta el contenido del archivo `schema.sql` que está en esta carpeta.
   *Esto creará la base de datos `gestion_tutor` y las tablas.*
3. Si tu contraseña de MySQL no es vacía, abre el archivo `database.js` y pon tu contraseña donde dice `password: ''`.

## 4. Iniciar el Servidor
Ahora sí, enciende el sistema:
1. En la terminal, escribe:
   ```bash
   node server.js
   ```
2. Deberías ver un mensaje: `Server running on http://localhost:3000`

## 5. Usar la App
No abras el archivo haciendo doble clic.
1. Ve a tu navegador (Chrome/Edge).
2. Entra a: `http://localhost:3000`

¡Listo! Ahora el Login intentará conectarse a la base de datos real.
