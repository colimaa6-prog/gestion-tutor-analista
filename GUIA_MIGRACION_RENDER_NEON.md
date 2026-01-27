# Guía de Migración de Railway a Render + Neon (Plan Gratuito)

Esta guía te ayudará a migrar tu aplicación de Railway a una combinación de servicios **gratuitos y permanentes**:
- **Render**: Para alojar el código (Frontend y Backend Python).
- **Neon**: Para la base de datos PostgreSQL gratuita.

Esta solución es compatible con tu flujo de trabajo actual en GitHub.

---

## Parte 1: Preparar el Código

Antes de migrar, necesitamos hacer pequeños ajustes para optimizar la app en Render.

### 1. Actualizar `requirements.txt`
Hemos agregado `gunicorn` para un mejor rendimiento en producción.
(Ya realizado por el asistente).

### 2. Actualizar `Procfile`
Hemos cambiado el comando de inicio para usar `gunicorn`.
(Ya realizado por el asistente).

---

## Parte 2: Configurar la Base de Datos (Neon)

Railway ya no ofrece base de datos gratuita permanente, así que usaremos **Neon**, que es excelente y gratuito.

1. Ve a [neon.tech](https://neon.tech) y regístrate (puedes usar tu cuenta de GitHub).
2. Crea un nuevo proyecto (dale un nombre, ej: `gestion-tutor`).
3. Se te mostrará un "Connection String" (cadena de conexión) que se ve así:
   `postgres://usuario:password@ep-algo.aws.neon.tech/neondb?sslmode=require`
4. **Copia este string**, lo necesitarás en el siguiente paso.

---

## Parte 3: Configurar el Servidor (Render)

1. Ve a [dashboard.render.com](https://dashboard.render.com) y regístrate con tu cuenta de GitHub.
2. Haz clic en **"New +"** y selecciona **"Web Service"**.
3. Selecciona **"Build and deploy from a Git repository"**.
4. Conecta tu cuenta de GitHub y selecciona el repositorio de tu proyecto (`gestion-tutor-analista`).
5. Configura los siguientes detalles:
   - **Name**: El nombre que quieras (ej: `gestion-tutor`).
   - **Region**: Oregon (US West) o la que prefieras.
   - **Branch**: `main` (o la rama que uses).
   - **Runtime**: **Python 3**.
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: **Free**.

6. **Variables de Entorno (Environment Variables)**:
   Haz clic en "Advanced" o baja hasta la sección de variables y añade:
   
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | Pega aquí la conexión que copiaste de **Neon**. |
   | `PYTHON_VERSION` | `3.10.12` (o la versión que prefieras). |

7. Haz clic en **"Create Web Service"**.

---

## Parte 4: Migrar los Datos (Opcional pero recomendado)

Tu nueva base de datos en Neon está vacía. Necesitas crear las tablas.

1. **Opción Automática (Si tu app crea tablas al inicio):**
   Render desplegará la app. Si tu código tiene `init_db` o similar al arrancar, se crearán las tablas.
   
2. **Opción Manual (Recomendada):**
   Conecta a tu base de datos Neon usando cualquier cliente SQL (DBeaver, TablePlus, o incluso desde la terminal si tienes `psql`) usando la URL de conexión.
   Ejecuta el contenido de tu archivo `schema.sql` (o la estructura actual que tengas) para crear las tablas.

   Si tienes script de semillas (`seed_users.js` o similar), deberás ejecutarlo localmente pero apuntando a la nueva base de datos de Neon, o insertar los datos manualmente.

   **Tip:** Para correr scripts locales contra la nueva DB, crea un archivo `.env` local con:
   `DATABASE_URL=tu_url_de_neon_aqui`
   Y corre tus scripts de migración/seed.

---

## Resumen
Ahora tienes:
1. Tu código en GitHub.
2. Render observando GitHub: cada vez que hagas `git push`, Render actualizará la página web automáticamente.
3. Neon alojando tus datos de forma gratuita y persistente.
