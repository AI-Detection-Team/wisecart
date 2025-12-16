#!/usr/bin/env python3
"""
SQL Server Veritabanı Oluşturma Scripti
macOS için Docker SQL Server ile çalışır
"""

import subprocess
import time
import sys

def create_database():
    print("🗄️ WiseCartDB veritabanı oluşturuluyor...")
    
    # SQL komutunu hazırla
    sql_command = """
    IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'WiseCartDB')
    BEGIN
        CREATE DATABASE WiseCartDB;
        PRINT 'WiseCartDB veritabanı oluşturuldu.';
    END
    ELSE
    BEGIN
        PRINT 'WiseCartDB veritabanı zaten mevcut.';
    END
    """
    
    # Docker exec ile SQL komutunu çalıştır
    # SQL Server 2022'de sqlcmd farklı yerde olabilir
    commands = [
        # Yeni yol (SQL Server 2022)
        ['docker', 'exec', '-i', 'wisecart-sql', '/opt/mssql-tools18/bin/sqlcmd', 
         '-S', 'localhost', '-U', 'sa', '-P', 'WiseCart123!', '-Q', sql_command],
        # Eski yol
        ['docker', 'exec', '-i', 'wisecart-sql', '/opt/mssql-tools/bin/sqlcmd', 
         '-S', 'localhost', '-U', 'sa', '-P', 'WiseCart123!', '-Q', sql_command],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Veritabanı başarıyla oluşturuldu!")
                print(result.stdout)
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            continue
    
    # Alternatif: pyodbc kullan
    try:
        import pyodbc
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost,1433;'
            'DATABASE=master;'
            'UID=sa;'
            'PWD=WiseCart123!;'
            'TrustServerCertificate=yes;'
        )
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'WiseCartDB')
            CREATE DATABASE WiseCartDB
        """)
        conn.commit()
        print("✅ Veritabanı pyodbc ile oluşturuldu!")
        return True
    except ImportError:
        print("⚠️ pyodbc yüklü değil. 'pip install pyodbc' komutu ile yükleyin.")
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    print("⚠️ Veritabanı oluşturulamadı. Manuel olarak oluşturun:")
    print("   SQL Server Management Studio veya Azure Data Studio ile bağlanın")
    print("   Server: localhost,1433")
    print("   Username: sa")
    print("   Password: WiseCart123!")
    print("   CREATE DATABASE WiseCartDB; komutunu çalıştırın")
    return False

if __name__ == "__main__":
    # SQL Server'ın hazır olmasını bekle
    print("⏳ SQL Server'ın hazır olması bekleniyor...")
    time.sleep(5)
    
    create_database()


