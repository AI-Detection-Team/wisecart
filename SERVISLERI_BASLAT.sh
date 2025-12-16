#!/bin/bash

echo "🚀 WiseCart Tüm Servisleri Başlatılıyor..."
echo ""

# 1. SQL Server Docker Container
echo "📦 SQL Server Docker Container başlatılıyor..."
docker start wisecart-sql 2>/dev/null || docker run -d --name wisecart-sql --platform linux/amd64 -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=WiseCart123!" -e "MSSQL_PID=Express" -p 1433:1433 mcr.microsoft.com/mssql/server:2022-latest
sleep 5
echo "✅ SQL Server hazır"
echo ""

# 2. Python Flask API Server
echo "🐍 Python Flask API Server başlatılıyor..."
cd /Users/pinareray/Desktop/wisecart/AI_Engine
pkill -f "python3 api_server.py" 2>/dev/null
python3 api_server.py > /tmp/wisecart_api.log 2>&1 &
sleep 3
echo "✅ Python API hazır (Port 5001)"
echo ""

# 3. Python SOAP Server
echo "🌐 Python SOAP Server başlatılıyor..."
cd /Users/pinareray/Desktop/wisecart/AI_Engine
pkill -f "python3 soap_server.py" 2>/dev/null
python3 soap_server.py > /tmp/wisecart_soap.log 2>&1 &
sleep 2
echo "✅ SOAP Server hazır (Port 8000)"
echo ""

# 4. Python gRPC Server
echo "📡 Python gRPC Server başlatılıyor..."
cd /Users/pinareray/Desktop/wisecart/AI_Engine
pkill -f "python3 grpc_server.py" 2>/dev/null
python3 grpc_server.py > /tmp/wisecart_grpc.log 2>&1 &
sleep 2
echo "✅ gRPC Server hazır (Port 50051)"
echo ""

# 5. Node.js Log Service
echo "📝 Node.js Log Service başlatılıyor..."
cd /Users/pinareray/Desktop/wisecart/Log_Service
pkill -f "node server.js" 2>/dev/null
node server.js > /tmp/wisecart_log.log 2>&1 &
sleep 2
echo "✅ Node.js Log Service hazır (Port 4000)"
echo ""

# 6. .NET Web Application
echo "🌐 .NET Web Application başlatılıyor..."
cd /Users/pinareray/Desktop/wisecart/WiseCart_Web
pkill -f "dotnet run" 2>/dev/null
sleep 2
ASPNETCORE_ENVIRONMENT=Development dotnet run --urls "http://localhost:5133" > /tmp/wisecart_web.log 2>&1 &
sleep 10
echo "✅ .NET Web Application hazır (Port 5133)"
echo ""

echo "🎉 Tüm servisler başlatıldı!"
echo ""
echo "📊 Servis Durumu:"
echo "  - Python API: http://localhost:5001"
echo "  - SOAP Server: http://localhost:8000"
echo "  - gRPC Server: localhost:50051"
echo "  - Node.js Log: http://localhost:4000"
echo "  - .NET Web: http://localhost:5133"
echo ""
echo "🌐 Web sitesini açın: http://localhost:5133"



