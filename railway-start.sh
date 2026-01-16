#!/bin/bash
set -e

echo "🚀 Iniciando despliegue en Railway..."

# Crear carpeta wallet
mkdir -p wallet

# Decodificar archivos del wallet desde variables de entorno
if [ ! -z "$WALLET_CWALLET_SSO" ]; then
    echo "📁 Decodificando Wallet..."
    echo $WALLET_CWALLET_SSO | base64 -d > wallet/cwallet.sso
    echo $WALLET_EWALLET_P12 | base64 -d > wallet/ewallet.p12
    echo $WALLET_TNSNAMES_ORA | base64 -d > wallet/tnsnames.ora
    echo $WALLET_SQLNET_ORA | base64 -d > wallet/sqlnet.ora
    echo $WALLET_OJDBC_PROPERTIES | base64 -d > wallet/ojdbc.properties
    export ORACLE_WALLET_LOCATION=$PWD/wallet
    echo "✅ Wallet configurado"
else
    echo "⚠️  Wallet no encontrado en variables de entorno"
fi

# Iniciar la aplicación
echo "🎯 Iniciando servidor Node.js..."
node server.js
