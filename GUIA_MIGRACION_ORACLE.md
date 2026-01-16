# 🚀 GUÍA DE MIGRACIÓN A ORACLE AUTONOMOUS DATABASE

## 📋 **PASO 1: Ejecutar Scripts en Oracle Cloud**

### 1.1 Acceder a Oracle Cloud
1. Ve a: https://cloud.oracle.com
2. Inicia sesión con tu cuenta
3. Ve a **Database Actions** → **SQL**

### 1.2 Crear el Esquema
1. Abre el archivo: `schema_oracle_migration.sql`
2. Copia TODO el contenido
3. Pégalo en SQL Developer Web
4. Click en **"Run Script"** (botón verde ▶)
5. Espera a que termine (debería decir "✅ Schema creado exitosamente")

### 1.3 Importar los Datos
1. Abre el archivo: `data_migration_oracle.sql`
2. Copia TODO el contenido
3. Pégalo en SQL Developer Web
4. Click en **"Run Script"**
5. Espera a que termine (debería decir "✅ Datos importados exitosamente")

---

## 📦 **PASO 2: Instalar Driver de Oracle**

Ejecuta en tu terminal:

```powershell
npm install oracledb
```

---

## 🔧 **PASO 3: Configurar Credenciales**

### 3.1 Descargar Wallet de Oracle
1. En Oracle Cloud, ve a tu Autonomous Database
2. Click en **"DB Connection"**
3. Descarga el **Wallet** (archivo ZIP)
4. Extrae el ZIP en una carpeta: `C:\oracle_wallet\`

### 3.2 Actualizar .env
Edita el archivo `.env` y agrega:

```env
# Oracle Database Configuration
ORACLE_USER=ADMIN
ORACLE_PASSWORD=tu_contraseña_de_oracle
ORACLE_CONNECT_STRING=rggestiontutor_high
ORACLE_WALLET_LOCATION=C:\\oracle_wallet
```

---

## 🔄 **PASO 4: Cambiar el Código**

Ya he creado el archivo `database-oracle.js` que reemplazará a `database.js`.

Para activarlo:

1. Renombra `database.js` a `database-sqlite.js` (backup)
2. Renombra `database-oracle.js` a `database.js`
3. Reinicia el servidor Node.js

---

## ✅ **PASO 5: Probar Localmente**

1. Reinicia el servidor: `node server.js`
2. Abre: `http://localhost:3000`
3. Intenta hacer login
4. Verifica que todo funcione correctamente

---

## 🌐 **PASO 6: Desplegar en la Nube**

### Opción A: Oracle Cloud VM (Recomendado)
- Esperar a que haya capacidad de VM ARM
- Subir el código a la VM
- Configurar Nginx como reverse proxy
- Listo!

### Opción B: Railway.app (Temporal)
1. Crea cuenta en https://railway.app
2. Conecta tu repositorio de GitHub
3. Configura las variables de entorno
4. Deploy automático

---

## 📊 **Ventajas de Oracle vs SQLite**

| Característica | SQLite | Oracle |
|---|---|---|
| Usuarios concurrentes | ❌ 1 | ✅ Miles |
| En la nube | ❌ No | ✅ Sí |
| Backups automáticos | ❌ No | ✅ Sí |
| Escalabilidad | ❌ Limitada | ✅ Ilimitada |
| Costo | Gratis | Gratis (Always Free) |

---

## 🆘 **Troubleshooting**

### Error: "ORA-12154: TNS:could not resolve the connect identifier"
- Verifica que el Wallet esté en la ubicación correcta
- Verifica que `ORACLE_CONNECT_STRING` sea correcto

### Error: "ORA-01017: invalid username/password"
- Verifica las credenciales en `.env`
- Asegúrate de usar el usuario `ADMIN`

### Error: "Cannot find module 'oracledb'"
- Ejecuta: `npm install oracledb`

---

## 📝 **Próximos Pasos**

1. ✅ Ejecutar `schema_oracle_migration.sql` en Oracle Cloud
2. ✅ Ejecutar `data_migration_oracle.sql` en Oracle Cloud
3. ✅ Instalar `oracledb`: `npm install oracledb`
4. ✅ Descargar y configurar Wallet
5. ✅ Actualizar `.env` con credenciales
6. ✅ Activar `database-oracle.js`
7. ✅ Probar localmente
8. ✅ Desplegar en la nube

---

**¿Listo para empezar?** 🚀
