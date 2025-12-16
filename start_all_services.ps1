# WiseCart - Tüm Servisleri Başlatma Scripti (Windows PowerShell)
# Bu script tüm servisleri tek seferde başlatır

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WiseCart - Tüm Servisleri Başlatılıyor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Proje dizinine git
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 1. Python Flask API Server (Port 5000)
Write-Host "[1/5] Python Flask API Server başlatılıyor (Port 5000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\AI_Engine'; python api_server.py" -WindowStyle Normal
Start-Sleep -Seconds 3
Write-Host "    ✓ Python API başlatıldı" -ForegroundColor Green
Write-Host ""

# 2. Python SOAP Server (Port 8000)
Write-Host "[2/5] Python SOAP Server başlatılıyor (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\AI_Engine'; python soap_server.py" -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host "    ✓ SOAP Server başlatıldı" -ForegroundColor Green
Write-Host ""

# 3. Python gRPC Server (Port 50051)
Write-Host "[3/5] Python gRPC Server başlatılıyor (Port 50051)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\AI_Engine'; python grpc_server.py" -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host "    ✓ gRPC Server başlatıldı" -ForegroundColor Green
Write-Host ""

# 4. Node.js Log Service (Port 4000)
Write-Host "[4/5] Node.js Log Service başlatılıyor (Port 4000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\Log_Service'; node server.js" -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host "    ✓ Node.js Log Service başlatıldı" -ForegroundColor Green
Write-Host ""

# 5. .NET Web Application (Port 5133)
Write-Host "[5/5] .NET Web Application başlatılıyor (Port 5133)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\WiseCart_Web'; dotnet watch run" -WindowStyle Normal
Start-Sleep -Seconds 5
Write-Host "    ✓ .NET Web Application başlatıldı" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tüm Servisler Başlatıldı!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Servisler:" -ForegroundColor White
Write-Host "  - Python API:        http://localhost:5000" -ForegroundColor Cyan
Write-Host "  - SOAP Server:       http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - gRPC Server:       localhost:50051" -ForegroundColor Cyan
Write-Host "  - Node.js Log:       http://localhost:4000" -ForegroundColor Cyan
Write-Host "  - .NET Web:          http://localhost:5133" -ForegroundColor Cyan
Write-Host ""
Write-Host "Web sitesini açın: " -NoNewline
Write-Host "http://localhost:5133" -ForegroundColor Yellow
Write-Host ""
Write-Host "NOT: Servisleri durdurmak için açılan pencereleri kapatın." -ForegroundColor Gray
Write-Host ""
Write-Host "Devam etmek için bir tuşa basın..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


