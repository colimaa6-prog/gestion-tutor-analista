# Guía de Conexión a Oracle Cloud

## Problema Detectado: Incompatibilidad de Wallet con Node.js v24

Hemos detectado que el "Thin Mode" (modo ligero) de Oracle en Node.js v24 tiene problemas para desencriptar el Wallet de Oracle Cloud (`bad decrypt`), debido a cambios recientes en la seguridad de OpenSSL.

**La SOLUCIÓN DEFINITIVA es instalar el "Oracle Instant Client" (modo nativo).**

Sigue estos pasos sencillos:

### 1. Descargar Oracle Instant Client
1. Ve a la página oficial: [Oracle Instant Client for Windows x64](https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html)
2. Descarga el archivo **"Basic Light Package"** (ZIP). (Suele ser el segundo o tercero de la lista, aprox 50MB).
   - *Nota: No necesitas cuenta para "Basic Light" habitualmente, pero si te pide, usa una gratuita o busca el enlace directo.*
   - Enlace directo probable: [Click aquí para descargar 21c Basic Light](https://download.oracle.com/otn_software/nt/instantclient/2113000/instantclient-basiclite-windows.x64-21.13.0.0.0dbru.zip)

### 2. Instalar (Descomprimir)
1. Crea una carpeta llamada `C:\oracle`.
2. Mueve el ZIP descargado ahí y descomprímelo.
3. Deberías tener una carpeta como `C:\oracle\instantclient_21_13` (o similar).
4. **Copia esa ruta**.

### 3. Configurar Windows
1. Abre el menú Inicio y busca **"Variables de entorno"** (o "Editar las variables de entorno del sistema").
2. Haz clic en el botón **"Variables de entorno..."**.
3. En la lista de abajo ("Variables del sistema"), busca la variable **Path** y dale **Editar**.
4. Haz clic en **Nuevo** y pega la ruta: `C:\oracle\instantclient_21_13` (Asegúrate que coincida con tu carpeta real).
5. Acepta todo para cerrar.

### 4. Reiniciar
1. **Reinicia tu computadora** (o al menos cierra y vuelve a abrir Visual Studio Code y todas las terminales) para que reconozca el cambio.

### 5. Probar
Una vez hecho esto, avísame y ejecutaré la prueba final. Con el Instant Client instalado, el error de `bad decrypt` desaparecerá.
