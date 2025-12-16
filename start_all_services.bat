@echo off
REM WiseCart - Tüm Servisleri Başlatma Scripti (Windows)
REM Bu script tüm servisleri tek seferde başlatır

echo.
echo ========================================
echo   WiseCart - Tüm Servisleri Başlatılıyor
echo ========================================
echo.

REM Proje dizinine git
cd /d "%~dp0"

REM 1. Python Flask API Server (Port 5000)
echo [1/5] Python Flask API Server başlatılıyor (Port 5000)...
start "WiseCart - Python API" cmd /k "cd AI_Engine && python api_server.py"
timeout /t 3 /nobreak >nul
echo    ✓ Python API başlatıldı
echo.

REM 2. Python SOAP Server (Port 8000)
echo [2/5] Python SOAP Server başlatılıyor (Port 8000)...
start "WiseCart - SOAP Server" cmd /k "cd AI_Engine && python soap_server.py"
timeout /t 2 /nobreak >nul
echo    ✓ SOAP Server başlatıldı
echo.

REM 3. Python gRPC Server (Port 50051)
echo [3/5] Python gRPC Server başlatılıyor (Port 50051)...
start "WiseCart - gRPC Server" cmd /k "cd AI_Engine && python grpc_server.py"
timeout /t 2 /nobreak >nul
echo    ✓ gRPC Server başlatıldı
echo.

REM 4. Node.js Log Service (Port 4000)
echo [4/5] Node.js Log Service başlatılıyor (Port 4000)...
start "WiseCart - Node.js Log" cmd /k "cd Log_Service && node server.js"
timeout /t 2 /nobreak >nul
echo    ✓ Node.js Log Service başlatıldı
echo.

REM 5. .NET Web Application (Port 5133)
echo [5/5] .NET Web Application başlatılıyor (Port 5133)...
start "WiseCart - .NET Web" cmd /k "cd WiseCart_Web && dotnet watch run"
timeout /t 5 /nobreak >nul
echo    ✓ .NET Web Application başlatıldı
echo.

echo ========================================
echo   Tüm Servisler Başlatıldı!
echo ========================================
echo.
echo Servisler:
echo   - Python API:        http://localhost:5000
echo   - SOAP Server:       http://localhost:8000
echo   - gRPC Server:       localhost:50051
echo   - Node.js Log:       http://localhost:4000
echo   - .NET Web:          http://localhost:5133
echo.
echo Web sitesini açın: http://localhost:5133
echo.
echo NOT: Servisleri durdurmak için açılan pencereleri kapatın.
echo.
pause


