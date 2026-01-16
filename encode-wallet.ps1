# Script para codificar archivos del Wallet en Base64
# Ejecuta este script y copia el output a las variables de entorno de Railway

Write-Host "🔐 Codificando archivos del Wallet en Base64..." -ForegroundColor Cyan
Write-Host ""

$walletPath = ".\wallet"

if (!(Test-Path $walletPath)) {
    Write-Host "❌ Error: No se encontró la carpeta 'wallet'" -ForegroundColor Red
    exit 1
}

$files = @("cwallet.sso", "ewallet.p12", "tnsnames.ora", "sqlnet.ora", "ojdbc.properties")

Write-Host "📋 Copia estas variables de entorno en Railway:" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Yellow
Write-Host ""

foreach ($file in $files) {
    $filePath = Join-Path $walletPath $file
    
    if (Test-Path $filePath) {
        $bytes = [IO.File]::ReadAllBytes($filePath)
        $base64 = [Convert]::ToBase64String($bytes)
        $varName = "WALLET_" + ($file.ToUpper() -replace '\.', '_')
        
        Write-Host "$varName=" -NoNewline -ForegroundColor Cyan
        Write-Host $base64 -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "⚠️  Archivo no encontrado: $file" -ForegroundColor Yellow
    }
}

Write-Host "================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Codificación completa!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Instrucciones:" -ForegroundColor Cyan
Write-Host "1. Copia cada línea de arriba" -ForegroundColor White
Write-Host "2. Ve a Railway → Variables" -ForegroundColor White
Write-Host "3. Pega cada variable (nombre=valor)" -ForegroundColor White
Write-Host ""
