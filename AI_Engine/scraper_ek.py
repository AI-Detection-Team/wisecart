from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random
import os

# --- DÜZELTİLMİŞ VE KONTROL EDİLMİŞ LİNKLER ---
CATEGORIES_TO_ADD = {
    # Televizyon için 'elektronik' ön eki kaldırıldı
    "Televizyon": "https://www.n11.com/televizyon-ve-ses-sistemleri/televizyon",
    
    # Akıllı Saat için 'giyilebilir-teknoloji' ara kategorisi eklendi
    "AkilliSaat": "https://www.n11.com/telefon-ve-aksesuarlari/giyilebilir-teknoloji/akilli-saat",
    
    # Oyun Konsolu (Çalıştığı için aynı bırakıldı)
    "OyunKonsolu": "https://www.n11.com/video-oyun-konsol",
    
    # Kulaklık için en popüler ve dolu kategori olan 'Bluetooth Kulaklık' seçildi
    "Kulaklik": "https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu-aksesuarlari/bluetooth-kulaklik",
    
    # Yazıcı için kategori ismi 'yazici-tarayici-ve-aksesuarlari' olarak güncellendi
    "Yazici": "https://www.n11.com/bilgisayar/yazici-tarayici-ve-aksesuarlari/yazici",
    
}

MAX_PAGES = 30 
DELAY = 2

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--start-maximized")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_missing_data():
    driver = setup_driver()
    new_products = []
    
    print(f"🚀 EKSİK VERİ AVI BAŞLIYOR... (Hedef: {list(CATEGORIES_TO_ADD.keys())})")

    for cat_name, cat_url in CATEGORIES_TO_ADD.items():
        print(f"\n📂 EK KATEGORİ: {cat_name} taranıyor...")
        
        for page in range(1, MAX_PAGES + 1):
            current_url = f"{cat_url}?pg={page}"
            try:
                driver.get(current_url)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(DELAY + random.random()) 
                
                cards = driver.find_elements(By.CSS_SELECTOR, "li.column")
                
                if len(cards) == 0:
                    print(f"   ⚠️ Sayfa {page} boş veya yüklenmedi, geçiliyor.")
                    continue 

                print(f"   ├── Sayfa {page}: {len(cards)} ürün bulundu.")

                for card in cards:
                    try:
                        title = card.find_element(By.CLASS_NAME, "productName").text
                        try:
                            price_element = card.find_element(By.CSS_SELECTOR, ".newPrice ins")
                            price = price_element.text.strip()
                        except: price = "0"

                        try: link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except: link = ""
                        
                        brand = title.split(" ")[0]
                        
                        try:
                            rating_text = card.find_element(By.CLASS_NAME, "ratingText").text
                            rating_count = rating_text.replace("(", "").replace(")", "")
                        except: rating_count = "0"

                        if price != "0":
                            new_products.append({
                                "Kategori": cat_name,
                                "Marka": brand,
                                "Model": title,
                                "Fiyat": price,
                                "Yorum_Sayisi": rating_count,
                                "Link": link
                            })
                    except: continue
            except Exception as e:
                print(f"⚠️ Hata: {e}")
                continue

    driver.quit()
    return new_products

if __name__ == "__main__":
    # 1. Mevcut Dosyayı Oku
    EXISTING_FILE = "tum_urunler.csv" 
    
    if os.path.exists(EXISTING_FILE):
        print(f"📂 Mevcut dosya '{EXISTING_FILE}' okunuyor...")
        try:
            df_old = pd.read_csv(EXISTING_FILE)
            print(f"   -> Mevcut Kayıt Sayısı: {len(df_old)}")
        except:
            df_old = pd.DataFrame()
    else:
        print("⚠️ Mevcut dosya bulunamadı, sıfırdan başlanıyor.")
        df_old = pd.DataFrame()

    # 2. Yeni Verileri Çek
    new_data = scrape_missing_data()
    
    if len(new_data) > 0:
        df_new = pd.DataFrame(new_data)
        
        # 3. Birleştir
        df_final = pd.concat([df_old, df_new], ignore_index=True)
        
        # 4. Temizlik
        print("🧹 Veriler birleştiriliyor ve kopyalar siliniyor...")
        before_dedup = len(df_final)
        df_final.drop_duplicates(subset=['Link'], keep='first', inplace=True)
        
        # Fiyat Temizliği
        try:
            df_final['Fiyat'] = df_final['Fiyat'].astype(str).str.replace(" TL", "").str.replace("TL", "")
            df_final['Fiyat'] = df_final['Fiyat'].str.replace(".", "").str.replace(",", ".")
        except: pass

        # 5. Kaydet
        FINAL_FILE = "tum_urunler_final.csv" 
        df_final.to_csv(FINAL_FILE, index=False)
        
        print("\n" + "="*50)
        print(f"✅ İŞLEM TAMAMLANDI!")
        print(f"   - Eski Veri: {len(df_old)}")
        print(f"   - Yeni Çekilen: {len(df_new)}")
        print(f"   - Birleşim Sonrası (Toplam): {before_dedup}")
        print(f"   - Kopyalar Silindikten Sonra (Net): {len(df_final)}")
        print(f"   - Dosya: {FINAL_FILE}")
        print("="*50)
        print(df_final.groupby("Kategori").count())
    else:
        print("❌ Yeni veri çekilemedi. Linkleri veya internet bağlantınızı kontrol edin.")