from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random

# --- AYARLAR ---
CATEGORIES = {
    "Laptop": "https://www.n11.com/bilgisayar/dizustu-bilgisayar",
    "Telefon": "https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu",
    "Tablet": "https://www.n11.com/bilgisayar/tablet",
    "Televizyon": "https://www.n11.com/televizyon-ve-ses-sistemleri/televizyon",
    "AkilliSaat": "https://www.n11.com/telefon-ve-aksesuarlari/giyilebilir-teknoloji/akilli-saat",
    "OyunKonsolu": "https://www.n11.com/video-oyun-konsol",
    "Kulaklik": "https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu-aksesuarlari/bluetooth-kulaklik",
    "Yazici": "https://www.n11.com/bilgisayar/yazici-tarayici-ve-aksesuarlari/yazici",
    "Monitor": "https://www.n11.com/bilgisayar/cevre-birimleri/monitor-ve-ekran"
}

MAX_PAGES = 50 # 50 Sayfa x 9 Kategori = ~10.000 Veri
DELAY = 1

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--start-maximized")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def clean_price(price_text):
    """
    Fiyatı temizler: '2.245,08 TL' -> 2245.08 (Float)
    """
    if not price_text: return 0.0
    try:
        # 1. TL ve boşlukları at
        clean = price_text.replace("TL", "").replace(" ", "").strip()
        # 2. Binlik ayracı olan noktayı sil (2.245 -> 2245)
        clean = clean.replace(".", "")
        # 3. Kuruş ayracı olan virgülü noktaya çevir (08 -> .08)
        clean = clean.replace(",", ".")
        return float(clean)
    except:
        return 0.0

def scrape_n11_v3():
    driver = setup_driver()
    all_products = []
    
    print(f"🚀 GÖRSELLİ VE HATASIZ VERİ AVI BAŞLIYOR...")

    for cat_name, cat_url in CATEGORIES.items():
        print(f"\n📂 KATEGORİ: {cat_name}")
        
        for page in range(1, MAX_PAGES + 1):
            current_url = f"{cat_url}?pg={page}"
            try:
                driver.get(current_url)
                # Sayfanın yavaşça altına in (Resimlerin yüklenmesi için şart!)
                for i in range(1, 5):
                    driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {i/5});")
                    time.sleep(0.5)
                
                cards = driver.find_elements(By.CSS_SELECTOR, "li.column")
                if not cards: break

                print(f"   ├── Sayfa {page}: {len(cards)} ürün.")

                for card in cards:
                    try:
                        # 1. İsim
                        title = card.find_element(By.CLASS_NAME, "productName").text
                        
                        # 2. Fiyat
                        price_element = card.find_element(By.CSS_SELECTOR, ".newPrice ins")
                        price_raw = price_element.text.strip()
                        price_val = clean_price(price_raw) # Anında temizle

                        # 3. Link
                        link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        
                        # 4. RESİM (YENİ!)
                        # N11 lazy-load kullanır, resim bazen 'src' bazen 'data-original' içindedir.
                        try:
                            img_tag = card.find_element(By.CSS_SELECTOR, ".cardImage img")
                            img_url = img_tag.get_attribute("data-original")
                            if not img_url:
                                img_url = img_tag.get_attribute("src")
                        except:
                            img_url = "https://via.placeholder.com/500?text=Resim+Yok"

                        # 5. Yorum ve Marka
                        try:
                            rating_text = card.find_element(By.CLASS_NAME, "ratingText").text
                            rating_count = rating_text.replace("(", "").replace(")", "")
                        except: rating_count = "0"
                        
                        brand = title.split(" ")[0]

                        if price_val > 0:
                            all_products.append({
                                "Kategori": cat_name,
                                "Marka": brand,
                                "Model": title,
                                "Fiyat": price_val, # Artık sayı olarak kaydediyoruz
                                "Yorum_Sayisi": rating_count,
                                "Link": link,
                                "Resim": img_url # Resim linki eklendi
                            })
                    except: continue
            except Exception as e:
                print(f"⚠️ Hata: {e}")
                continue

    driver.quit()
    return all_products

if __name__ == "__main__":
    data = scrape_n11_v3()
    
    if len(data) > 0:
        df = pd.DataFrame(data)
        # Kopyaları Sil
        df.drop_duplicates(subset=['Link'], keep='first', inplace=True)
        
        # Dosyayı Kaydet
        df.to_csv("tum_urunler_v3.csv", index=False)
        
        print("\n" + "="*50)
        print(f"✅ İŞLEM TAMAM! Toplam {len(df)} Eşsiz Ürün.")
        print(f"💾 Dosya: 'tum_urunler_v3.csv' (Resimli ve Düzgün Fiyatlı)")
        print("="*50)
    else:
        print("❌ Veri çekilemedi.")