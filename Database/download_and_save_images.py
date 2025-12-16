#!/usr/bin/env python3
"""
Ürün Görsellerini İndirip wwwroot/images/products Klasörüne Kaydetme Scripti
CSV'deki görsel URL'lerini indirir ve veritabanındaki ImageUrl'leri günceller
"""

import pandas as pd
import requests
import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Product
import urllib
import time

# macOS Docker SQL Server Ayarları
SERVER_NAME = "localhost,1433"
DATABASE_NAME = "WiseCartDB"
CSV_PATH = "../AI_Engine/tum_urunler_v3.csv"

# Görsellerin kaydedileceği klasör
IMAGES_DIR = "../WiseCart_Web/wwwroot/images/products"

# Bağlantı String (macOS Docker için)
try:
    import pymssql
    engine = create_engine(
        f"mssql+pymssql://sa:WiseCart123!@localhost:1433/{DATABASE_NAME}",
        echo=False
    )
    print("✅ pymssql ile bağlantı kuruldu")
except ImportError:
    print("⚠️ pymssql yüklü değil, pyodbc deneniyor...")
    try:
        params = urllib.parse.quote_plus(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE={DATABASE_NAME};"
            f"UID=sa;"
            f"PWD=WiseCart123!;"
            f"TrustServerCertificate=yes;"
        )
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        print("✅ pyodbc ile bağlantı kuruldu")
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        exit(1)

Session = sessionmaker(bind=engine)
session = Session()

def get_file_extension(url):
    """URL'den dosya uzantısını çıkarır"""
    parsed = urlparse(url)
    path = parsed.path
    ext = os.path.splitext(path)[1]
    if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        return '.jpg'  # Varsayılan uzantı
    return ext.lower()

def is_valid_image_url(url):
    """URL'nin geçerli bir görsel URL'si olup olmadığını kontrol eder"""
    if not url or url == "" or url == "nan":
        return False
    
    # Placeholder URL'lerini atla
    if 'via.placeholder.com' in url or 'placeholder' in url.lower():
        return False
    
    # Geçerli URL formatı kontrolü
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    return True

def download_image(url, save_path):
    """Görseli indirir ve kaydeder"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        # Content-Type kontrolü
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            return False
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Dosya boyutu kontrolü (çok küçük dosyalar muhtemelen hata sayfası)
        if os.path.getsize(save_path) < 100:
            os.remove(save_path)
            return False
        
        return True
    except requests.exceptions.RequestException as e:
        return False
    except Exception as e:
        return False

def process_images():
    """Görselleri indirir ve veritabanını günceller"""
    print("🚀 Görsel İndirme ve Kaydetme İşlemi Başlıyor...")
    print(f"📁 Hedef klasör: {IMAGES_DIR}")
    
    # Klasörü oluştur
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"✅ Klasör hazır: {IMAGES_DIR}")
    
    # CSV'yi oku
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"✅ CSV okundu: {len(df)} satır")
    except Exception as e:
        print(f"❌ CSV okuma hatası: {e}")
        return
    
    # Veritabanındaki tüm ürünleri al
    products = session.query(Product).all()
    product_dict = {}
    
    # Model/Name'e göre ürünleri eşleştir
    for product in products:
        key = product.Model or product.Name
        if key:
            product_dict[key.strip().lower()] = product
    
    print(f"✅ Veritabanında {len(product_dict)} ürün bulundu")
    
    # CSV'deki görselleri işle
    downloaded = 0
    skipped = 0
    failed = 0
    updated = 0
    
    # İlk 10 ürünü test et (isteğe bağlı - kaldırılabilir)
    # df = df.head(10)  # Test için ilk 10 ürün
    
    for idx, row in df.iterrows():
        try:
            # Model/Name kontrolü
            model_name = str(row.get('Model', row.get('Name', ''))).strip()
            if not model_name or model_name == "nan":
                skipped += 1
                continue
            
            # Ürünü bul
            product = product_dict.get(model_name.lower())
            if not product:
                skipped += 1
                continue
            
            # Görsel URL kontrolü
            img_url = ""
            if 'Resim' in df.columns and pd.notna(row.get('Resim')):
                img_url = str(row['Resim']).strip()
            
            # Geçersiz URL kontrolü
            if not is_valid_image_url(img_url):
                # Placeholder görsel kullan (eğer varsa)
                if os.path.exists(os.path.join(IMAGES_DIR, "placeholder.jpg")):
                    if not product.ImageUrl or product.ImageUrl.startswith('http'):
                        product.ImageUrl = "/images/products/placeholder.jpg"
                        session.commit()
                skipped += 1
                continue
            
            # Görsel zaten local path ise atla
            if img_url.startswith('/images/products/'):
                skipped += 1
                continue
            
            # Dosya adını oluştur (ürün ID + hash)
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            ext = get_file_extension(img_url)
            filename = f"product_{product.Id}_{url_hash}{ext}"
            filepath = os.path.join(IMAGES_DIR, filename)
            relative_path = f"/images/products/{filename}"
            
            # Eğer dosya zaten varsa atla
            if os.path.exists(filepath):
                product.ImageUrl = relative_path
                session.commit()
                skipped += 1
                continue
            
            # Görseli indir
            if (idx + 1) % 50 == 0 or downloaded < 10:
                print(f"   [{idx+1}/{len(df)}] İndiriliyor: {model_name[:50]}...")
            
            if download_image(img_url, filepath):
                # Veritabanını güncelle
                product.ImageUrl = relative_path
                session.commit()
                downloaded += 1
                updated += 1
                if downloaded <= 10 or downloaded % 50 == 0:
                    print(f"      ✅ [{downloaded}] Kaydedildi: {filename}")
            else:
                # İndirme başarısız, placeholder kullan (eğer varsa)
                if os.path.exists(os.path.join(IMAGES_DIR, "placeholder.jpg")):
                    if not product.ImageUrl or product.ImageUrl.startswith('http'):
                        product.ImageUrl = "/images/products/placeholder.jpg"
                        session.commit()
                failed += 1
                if failed <= 10 or failed % 100 == 0:
                    print(f"      ⚠️ [{failed}] İndirilemedi: {model_name[:30]}...")
            
            # Rate limiting (sunucuyu yormamak için)
            time.sleep(0.05)
            
        except Exception as e:
            print(f"   ⚠️ Hata (satır {idx+1}): {e}")
            failed += 1
            continue
    
    # Placeholder görsel oluştur (yoksa) - Basit SVG veya mevcut placeholder kullan
    placeholder_path = os.path.join(IMAGES_DIR, "placeholder.jpg")
    if not os.path.exists(placeholder_path):
        print("\n📝 Placeholder görsel oluşturuluyor...")
        # Basit bir placeholder görsel oluştur (PIL kullanarak)
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (500, 500), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            # Basit bir metin ekle
            try:
                # Font yoksa varsayılan kullan
                draw.text((250, 250), "Görsel Yok", fill='#999999', anchor='mm')
            except:
                pass
            img.save(placeholder_path, 'JPEG')
            print("✅ Placeholder görsel oluşturuldu")
        except ImportError:
            print("⚠️ PIL yüklü değil, placeholder görsel oluşturulamadı")
            print("   💡 Placeholder için: https://via.placeholder.com/500 kullanılacak")
    
    print("\n" + "="*60)
    print("📊 İşlem Özeti:")
    print(f"   ✅ İndirilen: {downloaded}")
    print(f"   ✅ Güncellenen: {updated}")
    print(f"   ⏭️  Atlanan: {skipped}")
    print(f"   ❌ Başarısız: {failed}")
    print(f"   📁 Toplam: {len(df)}")
    print("="*60)
    print("✅ İşlem tamamlandı!")

if __name__ == "__main__":
    process_images()
