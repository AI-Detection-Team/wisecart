#!/usr/bin/env python3
"""
Mevcut görselleri veritabanıyla eşleştirip ImageUrl'leri günceller
Dün çekilen görselleri veritabanına kaydeder
"""

import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Product

# macOS Docker SQL Server
try:
    import pymssql
    engine = create_engine(
        f"mssql+pymssql://sa:WiseCart123!@localhost:1433/WiseCartDB",
        echo=False
    )
    print("✅ pymssql ile bağlantı kuruldu")
except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")
    exit(1)

Session = sessionmaker(bind=engine)
session = Session()

def sync_images():
    """Mevcut görselleri veritabanıyla eşleştir"""
    print("🔄 Mevcut görselleri veritabanıyla eşleştiriliyor...")
    
    images_dir = "../WiseCart_Web/wwwroot/images/products"
    
    if not os.path.exists(images_dir):
        print(f"❌ Klasör bulunamadı: {images_dir}")
        return
    
    # Tüm görsel dosyalarını bul
    image_files = [f for f in os.listdir(images_dir) 
                   if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    print(f"📁 {len(image_files)} görsel dosyası bulundu")
    
    # Dosya adından ürün ID'sini çıkar: product_123_abc123.jpg -> 123
    pattern = re.compile(r'product_(\d+)_')
    
    updated = 0
    not_found = 0
    
    for filename in image_files:
        match = pattern.match(filename)
        if not match:
            continue
        
        product_id = int(match.group(1))
        relative_path = f"/images/products/{filename}"
        
        # Ürünü bul ve güncelle
        product = session.query(Product).filter(Product.Id == product_id).first()
        
        if product:
            # Sadece HTTP URL'si varsa güncelle (zaten local ise atla)
            if product.ImageUrl and product.ImageUrl.startswith('http'):
                product.ImageUrl = relative_path
                session.commit()
                updated += 1
                if updated <= 10 or updated % 100 == 0:
                    print(f"   ✅ [{updated}] Ürün ID {product_id} güncellendi")
        else:
            not_found += 1
            if not_found <= 5:
                print(f"   ⚠️ Ürün ID {product_id} bulunamadı (dosya: {filename})")
    
    print("\n" + "="*60)
    print("📊 İşlem Özeti:")
    print(f"   ✅ Güncellenen: {updated}")
    print(f"   ⚠️  Bulunamayan: {not_found}")
    print(f"   📁 Toplam dosya: {len(image_files)}")
    print("="*60)
    
    # Son durumu göster
    total = session.query(Product).count()
    local = session.query(Product).filter(Product.ImageUrl.like('/images/products/%')).count()
    http = session.query(Product).filter(Product.ImageUrl.like('http%')).count()
    
    print(f"\n📊 Güncel Durum:")
    print(f"   Toplam ürün: {total}")
    print(f"   Local görsel: {local}")
    print(f"   HTTP görsel (çekilecek): {http}")
    print("="*60)

if __name__ == "__main__":
    sync_images()




