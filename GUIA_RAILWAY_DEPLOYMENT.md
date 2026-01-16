# 🚀 GUÍA DE DESPLIEGUE EN RAILWAY.APP

## 📋 **Requisitos Previos**
- ✅ Cuenta de GitHub
- ✅ Cuenta de Railway.app
- ✅ Base de datos Oracle configurada
- ✅ Wallet de Oracle descargado

---

## 🎯 **PASO 1: Subir el código a GitHub**

### 1.1 Crear repositorio en GitHub
1. Ve a: https://github.com/new
2. Nombre del repositorio: `gestion-tutor-analista`
3. Visibilidad: **Private** (recomendado)
4. Click en **"Create repository"**

### 1.2 Subir el código
Ejecuta estos comandos en tu terminal (en la carpeta del proyecto):

```powershell
git init
git add .
git commit -m "Initial commit - Sistema de Gestión"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/gestion-tutor-analista.git
git push -u origin main
```

**Nota:** Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub.

---

## 🚂 **PASO 2: Desplegar en Railway**

### 2.1 Crear cuenta en Railway
1. Ve a: https://railway.app
2. Click en **"Login"**
3. Inicia sesión con GitHub
4. Autoriza Railway

### 2.2 Crear nuevo proyecto
1. Click en **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Busca y selecciona: `gestion-tutor-analista`
4. Click en **"Deploy Now"**

### 2.3 Configurar Variables de Entorno
1. En Railway, click en tu proyecto
2. Ve a la pestaña **"Variables"**
3. Agrega estas variables:

```
PORT=3000
ORACLE_USER=ADMIN
ORACLE_PASSWORD=mora1985
ORACLE_CONNECT_STRING=reportegestionvn_high
```

### 2.4 Subir el Wallet
Railway necesita el Wallet de Oracle. Hay dos opciones:

**Opción A: Codificar el Wallet en Base64**
1. En tu computadora, ejecuta:
```powershell
$walletFiles = Get-ChildItem "wallet\*"
foreach ($file in $walletFiles) {
    $base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($file.FullName))
    Write-Host "$($file.Name): $base64"
}
```

2. Copia cada archivo codificado y agrégalo como variable de entorno en Railway:
   - `WALLET_CWALLET_SSO` = (contenido base64 de cwallet.sso)
   - `WALLET_EWALLET_P12` = (contenido base64 de ewallet.p12)
   - `WALLET_TNSNAMES_ORA` = (contenido base64 de tnsnames.ora)
   - etc.

**Opción B: Usar Oracle Cloud Object Storage** (Más fácil)
1. Sube el wallet a un bucket público temporal
2. Descárgalo en el startup de Railway

---

## 🔧 **PASO 3: Configurar el Startup Script**

Crea un archivo `railway-start.sh`:

```bash
#!/bin/bash
# Descargar Oracle Instant Client
wget https://download.oracle.com/otn_software/linux/instantclient/2340000/instantclient-basic-linux.x64-23.4.0.24.05.zip
unzip instantclient-basic-linux.x64-23.4.0.24.05.zip
export LD_LIBRARY_PATH=$PWD/instantclient_23_4:$LD_LIBRARY_PATH

# Crear carpeta wallet
mkdir -p wallet

# Decodificar archivos del wallet (si usaste Opción A)
echo $WALLET_CWALLET_SSO | base64 -d > wallet/cwallet.sso
echo $WALLET_EWALLET_P12 | base64 -d > wallet/ewallet.p12
echo $WALLET_TNSNAMES_ORA | base64 -d > wallet/tnsnames.ora
# ... (repite para cada archivo)

export ORACLE_WALLET_LOCATION=$PWD/wallet
export ORACLE_INSTANT_CLIENT=$PWD/instantclient_23_4

# Iniciar la aplicación
node server.js
```

Actualiza el `Procfile`:
```
web: bash railway-start.sh
```

---

## ✅ **PASO 4: Verificar el Despliegue**

1. Railway te dará una URL como: `https://gestion-tutor-analista-production.up.railway.app`
2. Abre esa URL en tu navegador
3. Deberías ver la página de login
4. Intenta hacer login con:
   - Usuario: `HELDER MORA`
   - Contraseña: `Hmora`

---

## 🎉 **¡Listo!**

Tu aplicación ahora está en la nube y accesible desde cualquier lugar.

### **URLs Importantes:**
- **Aplicación:** https://tu-app.up.railway.app
- **Dashboard Railway:** https://railway.app/dashboard
- **Oracle Cloud:** https://cloud.oracle.com

---

## 🆘 **Troubleshooting**

### Error: "Cannot find module 'oracledb'"
- Asegúrate de que `package.json` tenga `oracledb` en dependencies
- Railway instalará automáticamente las dependencias

### Error: "NJS-517: Oracle Client library not found"
- Verifica que el script de startup descargue Instant Client
- Verifica que `LD_LIBRARY_PATH` esté configurado

### Error: "ORA-12154: TNS:could not resolve"
- Verifica que el Wallet esté correctamente decodificado
- Verifica que `ORACLE_WALLET_LOCATION` apunte a la carpeta correcta

---

## 💰 **Costos**

Railway te da **$5 de crédito gratis** cada mes, que es suficiente para:
- ~500 horas de ejecución
- Perfecto para 14 usuarios
- Si se acaba, cuesta ~$5/mes adicional

---

**¿Necesitas ayuda con algún paso?** 🚀
