# Guía de Conexión a Oracle Cloud (Actualizada)

Si tienes problemas para encontrar las opciones en Oracle Cloud, sigue estos pasos detallados.

## 1. Encontrar la opción "Download Wallet"

La interfaz de Oracle Cloud puede ser confusa. Sigue esta ruta:

1.  **Entra al Menú Principal**:
    Haz clic en el ícono de hamburguesa (tres líneas) en la esquina superior izquierda.

2.  **Navega a Autonomous Database**:
    - Ve a **Oracle Database**.
    - Haz clic en **Autonomous Database**.
    - *Si no ves tu base de datos, asegúrate de estar en el "Compartment" (Compartimiento) correcto en el menú desplegable de la izquierda.*

3.  **Entra a los DETALLES de tu Base de Datos**:
    - Verás una lista con tus bases de datos.
    - **Haz clic en el NOMBRE de tu base de datos** (en color azul). Esto te llevará a una nueva página con gráficos y detalles.

4.  **Localizar "Database Connection"**:
    - En la página de detalles, busca el botón **"Database connection"**.
    - Por lo general, está en la fila de botones superior (junto a "Service Console", "Stop", "Restart") o en una pestaña llamada "DB Connection".

5.  **Descargar**:
    - Se abrirá una ventana lateral o emergente.
    - Busca el botón **"Download Wallet"**.
    - Crea una contraseña (ej. `WalletPass123`) y descarga el ZIP.

---

## 2. Configuración en tu PC

Una vez tengas el archivo ZIP (ej. `Wallet_DBNAME.zip`):

1.  **Crear Carpeta**:
    Ve a la carpeta de tu proyecto: `C:\Users\HelderMoraCastellano\OneDrive - Exitus Credit\Aplicaciones\GESTION  PARA TUTOR ANALISTA\`
    Crea una carpeta llamada `wallet`.

2.  **Descomprimir**:
    Extrae **todos** los archivos del ZIP dentro de esa carpeta `wallet`.
    Deberías ver archivos como `tnsnames.ora`, `sqlnet.ora`, `cwallet.sso`.

3.  **Verificar tnsnames.ora**:
    Abre el archivo `wallet/tnsnames.ora` con el Bloc de Notas.
    Busca los nombres de servicio a la izquierda del `=`. Deberías ver algo como:
    `tubd_high = ...`
    `tubd_low = ...`
    Copia uno de esos nombres (ej. `tubd_high`).

---

## 3. Configurar el archivo `.env`

Abre el archivo `.env` en tu proyecto y asegúrate de que quede así:

```env
# Usuario de base de datos (por defecto suele ser ADMIN)
ORACLE_USER=ADMIN

# La contraseña que usas para entrar a esa base de datos (NO la del wallet, sino la de usuario ADMIN)
ORACLE_PASSWORD=TuPasswordDeBaseDeDatos

# El nombre del servicio que copiaste del tnsnames.ora
ORACLE_CONN_STR=tubd_high

# La ruta a la carpeta wallet que creaste (IMPORTANTE para que encuentre los archivos)
TNS_ADMIN=C:\Users\HelderMoraCastellano\OneDrive - Exitus Credit\Aplicaciones\GESTION  PARA TUTOR ANALISTA\wallet
```

---

## 4. Probar Conexión

Ejecuta el script de prueba de conexión e inicialización:

```powershell
npm run init-db
```

Si ves mensajes de error sobre "TNS:could not resolve service name", verifica que `TNS_ADMIN` apunta correctamente a la carpeta y que `ORACLE_CONN_STR` coincide exactamente con el nombre en `tnsnames.ora`.
