#!/usr/bin/env python3
"""
n11.com'dan Ürün Görsellerini Çekme ve Kaydetme Scripti
Ürün linklerinden görselleri çeker ve wwwroot/images/products klasörüne kaydeder
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import hashlib
import time
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Product
import urllib

# macOS Docker SQL Server Ayarları
SERVER_NAME = "localhost,1433"
DATABASE_NAME = "WiseCartDB"
CSV_PATH = "../AI_Engine/tum_urunler_v3.csv"
IMAGES_DIR = "../WiseCart_Web/wwwroot/images/products"

# Bağlantı String
try:
    import pymssql
    engine = create_engine(
        f"mssql+pymssql://sa:WiseCart123!@localhost:1433/{DATABASE_NAME}",
        echo=False
    )
    print("✅ pymssql ile bağlantı kuruldu")
except ImportError:
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
        return '.jpg'
    return ext.lower()

def extract_image_from_n11_selenium(url):
    """n11.com ürün sayfasından Selenium ile ana görseli çıkarır"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Arka planda çalış
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get(url)
            # Sayfanın yüklenmesini bekle
            time.sleep(2)
            
            # Görseli bul - n11.com'da genellikle şu selector'lar kullanılır
            img_url = None
            
            # n11.com ürün detay sayfasında görsel genellikle şu selector'larda:
            selectors = [
                (".cardImage img", ["data-original", "src"]),
                ("img[data-original]", ["data-original", "src"]),
                ("img[src*='urun']", ["src", "data-original"]),
                (".productImage img", ["src", "data-original"]),
                (".zoomImg", ["src", "data-original"]),
                ("img[class*='product']", ["src", "data-original"]),
            ]
            
            img_url = None
            for selector, attrs in selectors:
                try:
                    img_tag = driver.find_element(By.CSS_SELECTOR, selector)
                    for attr in attrs:
                        img_url = img_tag.get_attribute(attr)
                        if img_url and ('http' in img_url or img_url.startswith('//')):
                            break
                    if img_url:
                        break
                except:
                    continue
            
            # URL'yi temizle
            if img_url:
                if not img_url.startswith('http'):
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://www.n11.com' + img_url
                
                # Büyük boyutlu görsel al
                if 'thumb' in img_url:
                    img_url = img_url.replace('thumb', 'large')
                if 'small' in img_url:
                    img_url = img_url.replace('small', 'large')
            
            return img_url
            
        finally:
            driver.quit()
            
    except Exception as e:
        return None

def extract_image_from_n11(url):
    """n11.com ürün sayfasından ana görseli çıkarır (Selenium kullanır)"""
    return extract_image_from_n11_selenium(url)

def download_image(url, save_path):
    """Görseli indirir ve kaydeder"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            return False
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        if os.path.getsize(save_path) < 100:
            os.remove(save_path)
            return False
        
        return True
    except:
        return False

def process_images():
    """n11.com'dan görselleri çeker ve kaydeder"""
    print("🚀 n11.com'dan Görsel Çekme İşlemi Başlıyor...")
    print(f"📁 Hedef klasör: {IMAGES_DIR}")
    
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"✅ Klasör hazır: {IMAGES_DIR}")
    
    # CSV'yi oku
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"✅ CSV okundu: {len(df)} satır")
    except Exception as e:
        print(f"❌ CSV okuma hatası: {e}")
        return
    
    # Veritabanındaki ürünleri al
    products = session.query(Product).all()
    product_dict = {}
    for product in products:
        key = product.Model or product.Name
        if key:
            product_dict[key.strip().lower()] = product
    
    print(f"✅ Veritabanında {len(product_dict)} ürün bulundu")
    
    downloaded = 0
    skipped = 0
    failed = 0
    updated = 0
    
    # TÜM ÜRÜNLER İÇİN ÇALIŞTIR
    # Test için ilk 10 ürünü çekmek isterseniz: df = df.head(10)
    # Tümünü çekmek için aşağıdaki satırı yorum satırı yapın:
    # df = df.head(10)  # TEST İÇİN
    
    for idx, row in df.iterrows():
        try:
            model_name = str(row.get('Model', row.get('Name', ''))).strip()
            if not model_name or model_name == "nan":
                skipped += 1
                continue
            
            product = product_dict.get(model_name.lower())
            if not product:
                skipped += 1
                continue
            
            # Zaten local görsel varsa atla
            if product.ImageUrl and product.ImageUrl.startswith('/images/products/'):
                skipped += 1
                continue
            
            # HTTP görseli olmayan ürünleri atla (sadece HTTP görselleri çek)
            if not product.ImageUrl or not product.ImageUrl.startswith('http'):
                skipped += 1
                continue
            
            # Ürün linkini al
            product_url = str(row.get('Link', '')).strip()
            if not product_url or product_url == "nan" or 'n11.com' not in product_url:
                skipped += 1
                continue
            
            # İlerleme göster (her 10 üründe bir veya ilk 5'te)
            if (idx + 1) % 10 == 0 or (idx + 1) <= 5:
                print(f"   [{idx+1}/{len(df)}] İşleniyor: {model_name[:50]}...")
            
            # n11.com'dan görseli çek
            try:
                img_url = extract_image_from_n11(product_url)
            except Exception as e:
                img_url = None
                if failed < 5:
                    print(f"      ⚠️ Hata: {str(e)[:50]}...")
            
            if not img_url:
                failed += 1
                if failed <= 5 or failed % 100 == 0:
                    print(f"      ⚠️ [{failed}] Görsel bulunamadı: {model_name[:30]}...")
                time.sleep(0.5)  # Rate limiting
                continue
            
            # Dosya adını oluştur
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            ext = get_file_extension(img_url)
            filename = f"product_{product.Id}_{url_hash}{ext}"
            filepath = os.path.join(IMAGES_DIR, filename)
            relative_path = f"/images/products/{filename}"
            
            # Zaten varsa atla
            if os.path.exists(filepath):
                product.ImageUrl = relative_path
                session.commit()
                skipped += 1
                continue
            
            # Görseli indir
            if download_image(img_url, filepath):
                product.ImageUrl = relative_path
                session.commit()
                downloaded += 1
                updated += 1
                if downloaded <= 10 or downloaded % 50 == 0:
                    print(f"      ✅ [{downloaded}] Kaydedildi: {filename}")
            else:
                failed += 1
                if failed <= 5:
                    print(f"      ⚠️ İndirilemedi: {model_name[:30]}...")
            
            # Rate limiting (n11.com'u yormamak için)
            # Selenium zaten yavaş olduğu için kısa bekleme yeterli
            time.sleep(0.5)  # Her istek arasında 0.5 saniye bekle
            
            # Her 50 üründe bir özet göster
            if (downloaded + failed) % 50 == 0:
                print(f"\n   📊 İlerleme: {downloaded} indirildi, {failed} başarısız, {skipped} atlandı\n")
            
        except Exception as e:
            print(f"   ⚠️ Hata (satır {idx+1}): {e}")
            failed += 1
            continue
    
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


