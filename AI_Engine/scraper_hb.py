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
    "Laptop": "https://www.hepsiburada.com/laptop-notebook-dizustu-bilgisayarlar-c-98",
    "Telefon": "https://www.hepsiburada.com/cep-telefonlari-c-371965",
    "Tablet": "https://www.hepsiburada.com/tablet-c-3008012",
    "Televizyon": "https://www.hepsiburada.com/televizyonlar-c-163192",
    "AkilliSaat": "https://www.hepsiburada.com/akilli-saatler-c-60003676"
}

MAX_PAGES = 20  # Hepsiburada zorludur, az sayfayla deneyelim
DELAY = 5      # Bekleme süresini artırdık

def setup_driver():
    chrome_options = Options()
    # Bot algılamayı aşmak için kritik ayarlar
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    chrome_options.add_argument("--start-maximized")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_hepsiburada():
    driver = setup_driver()
    all_products = []
    
    print(f"🚀 HEPSİBURADA VERİ AVI BAŞLIYOR...")

    for cat_name, cat_url in CATEGORIES.items():
        print(f"\n📂 KATEGORİ: {cat_name}")
        
        for page in range(1, MAX_PAGES + 1):
            # Hepsiburada sayfa yapısı: ?sayfa=1
            current_url = f"{cat_url}?sayfa={page}"
            
            try:
                driver.get(current_url)
                # Sayfayı yavaşça aşağı kaydır (Lazy Load)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
                time.sleep(DELAY + random.random())
                
                # Ürün Kartlarını Bul (Genelde li etiketinde id'si 'i' ile başlayanlar)
                cards = driver.find_elements(By.CSS_SELECTOR, "li[id^='i']")
                
                # Eğer bulamazsa alternatif sınıf dene
                if len(cards) == 0:
                     cards = driver.find_elements(By.CLASS_NAME, "productListContent-item")

                print(f"   ├── Sayfa {page}: {len(cards)} ürün tarandı.")

                for card in cards:
                    try:
                        # Veri Çekme
                        try:
                            # İsim (Data Test ID ile daha garanti)
                            title = card.find_element(By.CSS_SELECTOR, "[data-test-id='product-card-name']").text
                        except: continue 

                        try:
                            price = card.find_element(By.CSS_SELECTOR, "[data-test-id='price-current-price']").text
                        except: 
                            price = "0"

                        try:
                            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except: link = ""
                        
                        # Marka (İsmin ilk kelimesi)
                        brand = title.split(" ")[0]
                        
                        # Hepsiburada yorum sayısını gizleyebiliyor, 0 varsayıyoruz
                        rating_count = "0" 

                        if price != "0":
                            all_products.append({
                                "Kategori": cat_name,
                                "Marka": brand,
                                "Model": title,
                                "Fiyat": price,
                                "Yorum_Sayisi": rating_count,
                                "Link": link,
                                "Kaynak": "Hepsiburada"
                            })
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Sayfa Hatası: {e}")
                continue

    driver.quit()
    return all_products

if __name__ == "__main__":
    # --- DÜZELTİLEN KISIM BURASI ---
    data = scrape_hepsiburada() # Artık doğru fonksiyonu çağırıyor
    
    if len(data) > 0:
        df = pd.DataFrame(data)
        
        # Fiyat Temizliği
        try:
            df['Fiyat'] = df['Fiyat'].str.replace(" TL", "").str.replace("TL", "").str.strip()
            df['Fiyat'] = df['Fiyat'].str.replace(".", "").str.replace(",", ".")
        except: pass

        df.to_csv("hepsiburada_urunler.csv", index=False)
        print(f"\n✅ BAŞARILI! {len(df)} ürün 'hepsiburada_urunler.csv' dosyasına kaydedildi.")
        print(df.head())
    else:
        print("❌ HATA: Hepsiburada'dan veri çekilemedi (Bot koruması aktif).")
        print("💡 İPUCU: N11 verisi (1300+ adet) projenin devamı için zaten yeterli. Hepsiburada olmazsa dert etme.")