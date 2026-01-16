# 🗄️ GUÍA: CONFIGURAR POSTGRESQL EN RAILWAY

## 📋 **PASO 1: Agregar PostgreSQL en Railway**

1. Ve a tu proyecto en Railway: https://railway.app
2. Click en **"+ New"** o **"Create"**
3. Selecciona **"Database"** → **"PostgreSQL"**
4. Railway creará automáticamente la base de datos
5. Espera a que termine de inicializarse (1-2 minutos)

---

## 🔗 **PASO 2: Conectar PostgreSQL al Servicio Web**

Railway automáticamente creará la variable `DATABASE_URL` y la compartirá con tu servicio web.

Para verificar:
1. Click en tu servicio **"web"**
2. Ve a **"Variables"**
3. Deberías ver `DATABASE_URL` (compartida desde PostgreSQL)

---

## 📊 **PASO 3: Inicializar el Esquema**

Railway tiene una consola SQL integrada:

1. Click en el servicio **"PostgreSQL"**
2. Ve a la pestaña **"Data"** o **"Query"**
3. Copia y pega el contenido de `init_postgres.sql`
4. Click en **"Run"** o **"Execute"**

Esto creará todas las tablas y datos iniciales.

---

## ✅ **PASO 4: Verificar que Funciona**

1. Railway redesplegará automáticamente tu app
2. Abre la URL de tu aplicación
3. Intenta hacer login:
   - Usuario: `HELDER MORA`
   - Contraseña: `Hmora`

---

## 🎯 **Ventajas de PostgreSQL vs SQLite:**

| Característica | SQLite | PostgreSQL |
|---|---|---|
| Usuarios concurrentes | ❌ 1 | ✅ Miles |
| Datos persistentes | ❌ Se pierden | ✅ Permanentes |
| En la nube | ❌ No | ✅ Sí |
| Backups automáticos | ❌ No | ✅ Sí |
| Escalabilidad | ❌ Limitada | ✅ Ilimitada |
| Costo en Railway | Gratis | Gratis |

---

## 🔄 **Migrar Datos de SQLite a PostgreSQL**

Si ya tienes datos en SQLite local que quieres migrar:

1. Exporta los datos de SQLite
2. Usa el script `init_postgres.sql` como base
3. Agrega tus datos al final del script
4. Ejecuta en Railway

---

## 🆘 **Troubleshooting:**

### Error: "relation 'users' does not exist"
- Ejecuta el script `init_postgres.sql` en Railway

### Error: "could not connect to server"
- Verifica que PostgreSQL esté corriendo en Railway
- Verifica que `DATABASE_URL` esté configurada

### Los datos se pierden al redesplegar
- Estás usando SQLite en lugar de PostgreSQL
- Agrega PostgreSQL en Railway y ejecuta `init_postgres.sql`

---

## 📝 **Próximos Pasos:**

1. ✅ Agregar PostgreSQL en Railway
2. ✅ Ejecutar `init_postgres.sql`
3. ✅ Verificar que funcione
4. ✅ ¡Listo! Datos persistentes en la nube

---

**¿Listo para agregar PostgreSQL en Railway?** 🚀
