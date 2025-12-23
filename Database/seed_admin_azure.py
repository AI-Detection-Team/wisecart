#!/usr/bin/env python3
"""
Admin kullanıcısı oluşturma scripti - Azure SQL için
"""

import subprocess
import time
import sys
import hashlib

def create_admin_azure():
    print("👤 Admin Kullanıcısı Oluşturuluyor (Azure SQL)...")
    
    # Admin bilgileri
    username = "admin"
    password_raw = "123456"
    email = "admin@wisecart.com"
    
    # Şifreyi MD5 ile hashle (C# kodundaki MD5Hash ile uyumlu)
    password_hash = hashlib.md5(password_raw.encode()).hexdigest()
    
    # SQL komutları
    sql_commands = f"""
    USE WiseCartDB;
    
    -- 1. Admin rolünü oluştur (yoksa)
    IF NOT EXISTS (SELECT * FROM Roles WHERE Name = 'Admin')
    BEGIN
        INSERT INTO Roles (Name) VALUES ('Admin');
        PRINT 'Admin rolü oluşturuldu.';
    END
    
    -- 2. Admin kullanıcısını oluştur (yoksa)
    IF NOT EXISTS (SELECT * FROM Users WHERE Username = '{username}')
    BEGIN
        DECLARE @AdminRoleId INT;
        SELECT @AdminRoleId = Id FROM Roles WHERE Name = 'Admin';
        
        INSERT INTO Users (Username, Email, PasswordHash, RoleId, CreatedAt)
        VALUES ('{username}', '{email}', '{password_hash}', @AdminRoleId, GETDATE());
        
        PRINT 'Admin kullanıcısı oluşturuldu.';
        PRINT 'Kullanıcı Adı: {username}';
        PRINT 'Şifre: {password_raw}';
    END
    ELSE
    BEGIN
        PRINT 'Admin kullanıcısı zaten mevcut.';
    END
    """
    
    # Docker exec ile SQL komutunu çalıştır
    commands = [
        ['docker', 'exec', '-i', 'wisecart-sql', '/opt/mssql-tools18/bin/sqlcmd', 
         '-S', 'localhost', '-U', 'sa', '-P', 'WiseCart123!', '-C', '-Q', sql_commands],
        ['docker', 'exec', '-i', 'wisecart-sql', '/opt/mssql-tools/bin/sqlcmd', 
         '-S', 'localhost', '-U', 'sa', '-P', 'WiseCart123!', '-C', '-Q', sql_commands],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Admin kullanıcısı başarıyla oluşturuldu!")
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
            'DATABASE=WiseCartDB;'
            'UID=sa;'
            'PWD=WiseCart123!;'
            'TrustServerCertificate=yes;'
        )
        cursor = conn.cursor()
        
        # Admin rolünü kontrol et ve oluştur
        cursor.execute("SELECT Id FROM Roles WHERE Name = 'Admin'")
        admin_role = cursor.fetchone()
        
        if not admin_role:
            cursor.execute("INSERT INTO Roles (Name) VALUES ('Admin')")
            conn.commit()
            cursor.execute("SELECT Id FROM Roles WHERE Name = 'Admin'")
            admin_role = cursor.fetchone()
            print("✅ Admin rolü oluşturuldu.")
        
        # Admin kullanıcısını kontrol et
        cursor.execute("SELECT Id FROM Users WHERE Username = ?", username)
        existing_user = cursor.fetchone()
        
        if not existing_user:
            cursor.execute("""
                INSERT INTO Users (Username, Email, PasswordHash, RoleId, CreatedAt)
                VALUES (?, ?, ?, ?, GETDATE())
            """, username, email, password_hash, admin_role[0])
            conn.commit()
            print(f"✅ Admin kullanıcısı başarıyla oluşturuldu!")
            print(f"   Kullanıcı Adı: {username}")
            print(f"   Şifre: {password_raw}")
        else:
            print("ℹ️ Admin kullanıcısı zaten mevcut.")
        
        conn.close()
        return True
    except ImportError:
        print("⚠️ pyodbc yüklü değil. 'pip install pyodbc' komutu ile yükleyin.")
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("\n⚠️ Manuel olarak Azure SQL'de şu komutu çalıştırın:")
        print(f"   INSERT INTO Users (Username, Email, PasswordHash, RoleId, CreatedAt)")
        print(f"   VALUES ('{username}', '{email}', '{password_hash}', (SELECT Id FROM Roles WHERE Name='Admin'), GETDATE());")
    
    return False

if __name__ == "__main__":
    print("⏳ SQL Server'ın hazır olması bekleniyor...")
    time.sleep(3)
    
    create_admin_azure()

