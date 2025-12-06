from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random

# --- AYARLAR (MEGA VERİ AVI - HEDEF 10.000) ---
CATEGORIES = {
    "Laptop": "https://www.n11.com/bilgisayar/dizustu-bilgisayar",
    "Masaustu": "https://www.n11.com/bilgisayar/masaustu-bilgisayar",
    "Telefon": "https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu",
    "Tablet": "https://www.n11.com/bilgisayar/tablet",
    "Televizyon": "https://www.n11.com/elektronik/televizyon-ve-ses-sistemleri/televizyon",
    "AkilliSaat": "https://www.n11.com/telefon-ve-aksesuarlari/akilli-saat-ve-bileklik",
    "Monitor": "https://www.n11.com/bilgisayar/cevre-birimleri/monitor-ve-ekran",
    "Kulaklik": "https://www.n11.com/arama?q=kulakl%C4%B1k",
    "OyunKonsolu": "https://www.n11.com/video-oyun-konsol/oyun-konsollari",
    "Yazici": "https://www.n11.com/bilgisayar/yazici-ve-sarf-malzemeleri/yazici"
}

# Hedef: 10 Kategori x 50 Sayfa = 500 Sayfa Tarama
MAX_PAGES_PER_CAT = 50 
DELAY = 1.5 # Hızlandırdık

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless") 
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_n11_mega():
    driver = setup_driver()
    all_products = []
    
    print(f"🚀 MEGA VERİ AVI BAŞLIYOR... (Hedef: 10.000+ Ürün)")

    for cat_name, cat_url in CATEGORIES.items():
        print(f"\n📂 KATEGORİ: {cat_name} taranıyor...")
        
        for page in range(1, MAX_PAGES_PER_CAT + 1):
            current_url = f"{cat_url}?pg={page}"
            try:
                driver.get(current_url)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(DELAY + random.random()) 
                
                cards = driver.find_elements(By.CSS_SELECTOR, "li.column")
                
                # Eğer sayfada ürün yoksa (kategori bitmişse) sonraki kategoriye geç
                if len(cards) == 0:
                    print(f"   ⚠️ Sayfa {page} boş, bu kategori bitti.")
                    break

                print(f"   ├── Sayfa {page}: {len(cards)} ürün bulundu.")

                for card in cards:
                    try:
                        title = card.find_element(By.CLASS_NAME, "productName").text
                        
                        try:
                            price_element = card.find_element(By.CSS_SELECTOR, ".newPrice ins")
                            price = price_element.text.strip()
                        except:
                            price = "0"

                        try: link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except: link = ""
                        
                        brand = title.split(" ")[0]
                        
                        try:
                            rating_text = card.find_element(By.CLASS_NAME, "ratingText").text
                            rating_count = rating_text.replace("(", "").replace(")", "")
                        except: rating_count = "0"

                        if price != "0":
                            all_products.append({
                                "Kategori": cat_name,
                                "Marka": brand,
                                "Model": title,
                                "Fiyat": price,
                                "Yorum_Sayisi": rating_count,
                                "Link": link
                            })
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Hata: {e}")
                continue

    driver.quit()
    return all_products

if __name__ == "__main__":
    data = scrape_n11_mega()
    
    if len(data) > 0:
        df = pd.DataFrame(data)
        
        # Kopyaları Sil
        df.drop_duplicates(subset=['Link'], keep='first', inplace=True)
        
        # Fiyat Temizliği
        try:
            df['Fiyat'] = df['Fiyat'].str.replace(" TL", "").str.replace("TL", "")
            df['Fiyat'] = df['Fiyat'].str.replace(".", "").str.replace(",", ".")
        except: pass

        df.to_csv("tum_urunler_mega.csv", index=False)
        
        print("\n" + "="*50)
        print(f"✅ MEGA GÖREV TAMAMLANDI! Toplam {len(df)} EŞSİZ ürün.")
        print("="*50)
        print(df.groupby("Kategori").count()) 
    else:
        print("❌ Hiç veri çekilemedi.")