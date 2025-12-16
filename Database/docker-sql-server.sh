#!/bin/bash

# SQL Server Docker Container Başlatma Scripti
# macOS için

echo "🐳 SQL Server Docker Container Başlatılıyor..."

# Eğer container zaten varsa durdur ve sil
docker stop wisecart-sql 2>/dev/null
docker rm wisecart-sql 2>/dev/null

# Yeni container oluştur ve başlat
docker run -d \
  --name wisecart-sql \
  -e "ACCEPT_EULA=Y" \
  -e "SA_PASSWORD=WiseCart123!" \
  -e "MSSQL_PID=Express" \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest

echo "⏳ SQL Server başlatılıyor (30 saniye bekleyin)..."
sleep 30

echo "✅ SQL Server hazır!"
echo "📝 Connection String:"
echo "Server=localhost,1433;Database=WiseCartDB;User Id=sa;Password=WiseCart123!;TrustServerCertificate=True;"


