#!/usr/bin/env python3
"""
Tabloları oluşturma scripti - SQL dosyasını parse eder
"""

import pymssql
import time
import re

def create_tables():
    print('📝 Tablolar oluşturuluyor...')
    time.sleep(5)
    
    try:
        conn = pymssql.connect(
            server='localhost', 
            port=1433, 
            user='sa', 
            password='WiseCart123!', 
            database='WiseCartDB', 
            autocommit=True
        )
        cursor = conn.cursor()
        
        # SQL dosyasını oku
        with open('create_all_tables.sql', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # GO komutlarını kaldır ve USE komutunu kaldır
        content = re.sub(r'USE\s+\w+;?\s*GO\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\bGO\b', ';', content, flags=re.IGNORECASE)
        
        # Her CREATE TABLE bloğunu bul ve çalıştır
        # IF NOT EXISTS bloğu içindeki CREATE TABLE'ı bul
        pattern = re.compile(r'IF NOT EXISTS.*?BEGIN\s*(CREATE TABLE.*?END)', re.DOTALL | re.IGNORECASE)
        
        matches = pattern.finditer(content)
        
        for match in matches:
            create_stmt = match.group(1).strip()
            # END'i kaldır
            create_stmt = re.sub(r'\s*END\s*;?\s*$', '', create_stmt, flags=re.IGNORECASE)
            
            # Tablo adını bul
            table_match = re.search(r'CREATE TABLE\s+\[dbo\]\.\[(\w+)\]', create_stmt, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                try:
                    # Önce tabloyu sil (varsa)
                    cursor.execute(f"IF OBJECT_ID('dbo.{table_name}', 'U') IS NOT NULL DROP TABLE [dbo].[{table_name}]")
                    # Sonra oluştur
                    cursor.execute(create_stmt)
                    print(f'   ✅ {table_name} tablosu oluşturuldu')
                except Exception as e:
                    print(f'   ⚠️ {table_name} hatası: {str(e)[:80]}')
        
        # Tablo sayısını kontrol et
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        table_count = cursor.fetchone()[0]
        print(f'\n✅ Toplam {table_count} tablo oluşturuldu!')
        
        conn.close()
        return table_count
        
    except Exception as e:
        print(f'❌ Hata: {str(e)[:300]}')
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    create_tables()
