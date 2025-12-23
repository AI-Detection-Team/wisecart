#!/usr/bin/env python3
"""
User tablosundan ProfileImagePath kolonunu kaldırır
Profil resmi kullanılmıyor, bu kolon gerekli değil
"""

import subprocess
import time
import sys

def remove_profile_image_path():
    print("🔧 User tablosundan ProfileImagePath kolonu kaldırılıyor...")
    
    sql_command = """
    USE WiseCartDB;
    
    IF EXISTS (
        SELECT * FROM sys.columns 
        WHERE object_id = OBJECT_ID(N'[dbo].[Users]') 
        AND name = 'ProfileImagePath'
    )
    BEGIN
        ALTER TABLE [dbo].[Users]
        DROP COLUMN ProfileImagePath;
        PRINT 'ProfileImagePath kolonu kaldırıldı.';
    END
    ELSE
    BEGIN
        PRINT 'ProfileImagePath kolonu zaten yok.';
    END
    """
    
    # Docker exec ile SQL komutunu çalıştır
    commands = [
        ['docker', 'exec', '-i', 'wisecart-sql', '/opt/mssql-tools18/bin/sqlcmd', 
         '-S', 'localhost', '-U', 'sa', '-P', 'WiseCart123!', '-Q', sql_command],
        ['docker', 'exec', '-i', 'wisecart-sql', '/opt/mssql-tools/bin/sqlcmd', 
         '-S', 'localhost', '-U', 'sa', '-P', 'WiseCart123!', '-Q', sql_command],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ ProfileImagePath kolonu başarıyla kaldırıldı!")
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
        
        # Kolonun var olup olmadığını kontrol et
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Users' 
            AND COLUMN_NAME = 'ProfileImagePath'
        """)
        
        if cursor.fetchone()[0] > 0:
            cursor.execute("""
                ALTER TABLE [dbo].[Users]
                DROP COLUMN ProfileImagePath
            """)
            conn.commit()
            print("✅ ProfileImagePath kolonu pyodbc ile kaldırıldı!")
        else:
            print("ℹ️ ProfileImagePath kolonu zaten yok.")
        
        conn.close()
        return True
    except ImportError:
        print("⚠️ pyodbc yüklü değil. 'pip install pyodbc' komutu ile yükleyin.")
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("\n⚠️ Manuel olarak SQL Server Management Studio veya Azure Data Studio ile bağlanın")
        print("   ve şu komutu çalıştırın:")
        print("   ALTER TABLE [dbo].[Users] DROP COLUMN ProfileImagePath;")
    
    return False

if __name__ == "__main__":
    print("⏳ SQL Server'ın hazır olması bekleniyor...")
    time.sleep(2)
    
    remove_profile_image_path()





