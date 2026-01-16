# 🐍 GUÍA: APLICACIÓN MIGRADA A PYTHON/FLASK

## ✅ **Cambios Realizados:**

1. **Backend migrado de Node.js a Python/Flask**
   - `server.js` → `app.py`
   - Todos los endpoints recreados
   - Soporte completo para Oracle Database

2. **Frontend sin cambios**
   - Los archivos HTML/JS siguen igual
   - No necesitas modificar nada

3. **Dependencias simplificadas**
   - Flask (framework web)
   - cx-Oracle (driver de Oracle)
   - flask-cors (CORS)
   - python-dotenv (variables de entorno)

---

## 🚀 **PASO 1: Instalar Dependencias**

```powershell
pip install -r requirements.txt
```

---

## 📦 **PASO 2: Instalar Oracle Instant Client**

Descarga Oracle Instant Client Basic:
- https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html

Extrae en: `C:\oracle\instantclient_23_4`

Agrega al PATH o configura en `.env`:
```
ORACLE_INSTANT_CLIENT=C:\oracle\instantclient_23_4
```

---

## ▶️ **PASO 3: Ejecutar Localmente**

```powershell
python app.py
```

La aplicación estará en: `http://localhost:3000`

---

## ☁️ **PASO 4: Desplegar en Railway**

### 4.1 Hacer commit y push

```powershell
git add .
git commit -m "Migrar de Node.js a Python/Flask"
git push
```

### 4.2 Railway detectará automáticamente

Railway verá `requirements.txt` y sabrá que es una app Python.

### 4.3 Variables de entorno

Ya están configuradas en Railway:
- `ORACLE_USER`
- `ORACLE_PASSWORD`
- `ORACLE_CONNECT_STRING`
- `WALLET_*` (todas las variables del wallet)
- `PORT`

---

## 🎯 **Ventajas de Python vs Node.js:**

| Característica | Node.js | Python |
|---|---|---|
| Instalación | Compleja | Ya instalado |
| Oracle Instant Client | Requerido | Requerido |
| Sintaxis | JavaScript | Python (más simple) |
| Despliegue Railway | Funciona | Funciona |
| Soporte Oracle | oracledb | cx-Oracle (mejor) |

---

## 🆘 **Troubleshooting:**

### Error: "No module named 'cx_Oracle'"
```powershell
pip install cx-Oracle
```

### Error: "DPI-1047: Cannot locate a 64-bit Oracle Client library"
- Descarga Oracle Instant Client
- Configura la variable `ORACLE_INSTANT_CLIENT` en `.env`

### Error: "ModuleNotFoundError: No module named 'flask'"
```powershell
pip install Flask
```

---

## 📝 **Próximos Pasos:**

1. ✅ Instalar dependencias: `pip install -r requirements.txt`
2. ✅ Probar localmente: `python app.py`
3. ✅ Hacer commit y push a GitHub
4. ✅ Railway redesplegará automáticamente
5. ✅ ¡Listo! La app estará en la nube

---

**¿Listo para probar?** 🚀
