from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random

# --- AYARLAR (BÜYÜK VERİ AVI) ---
# N11 Kategori Linkleri
CATEGORIES = {
    "Laptop": "https://www.n11.com/bilgisayar/dizustu-bilgisayar",
    "Telefon": "https://www.n11.com/telefon-ve-aksesuarlari/cep-telefonu",
    "Tablet": "https://www.n11.com/bilgisayar/tablet",
    "Televizyon": "https://www.n11.com/elektronik/televizyon-ve-ses-sistemleri/televizyon",
    "AkilliSaat": "https://www.n11.com/telefon-ve-aksesuarlari/akilli-saat-ve-bileklik"
}

# Sayfa Sayısı: Her kategoriden 25 sayfa x ~24 ürün = ~3000 Veri
MAX_PAGES_PER_CAT = 35
DELAY = 2 # Sayfalar arası bekleme süresi

def setup_driver():
    chrome_options = Options()
    # Bot olduğumuzu gizleyen ayarlar (Anti-Bot Detection)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless") # Hızlandırmak isterseniz bu satırı açın (Tarayıcı gizlenir)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_n11_final():
    driver = setup_driver()
    all_products = []
    
    print(f"🚀 BÜYÜK VERİ AVI BAŞLIYOR... (Hedef: 5 Kategori x {MAX_PAGES_PER_CAT} Sayfa)")

    for cat_name, cat_url in CATEGORIES.items():
        print(f"\n📂 KATEGORİ: {cat_name} taranıyor...")
        
        for page in range(1, MAX_PAGES_PER_CAT + 1):
            current_url = f"{cat_url}?pg={page}"
            try:
                driver.get(current_url)
                
                # Sayfanın altına in ki resimler/fiyatlar yüklensin (Lazy Load)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(DELAY + random.random()) 
                
                # Ürün Kartlarını Bul
                cards = driver.find_elements(By.CSS_SELECTOR, "li.column")
                print(f"   ├── Sayfa {page}: {len(cards)} ürün bulundu.")

                for card in cards:
                    try:
                        # 1. Ürün Adı
                        title = card.find_element(By.CLASS_NAME, "productName").text
                        
                        # 2. Fiyat (İndirimli olanı al)
                        try:
                            price_element = card.find_element(By.CSS_SELECTOR, ".newPrice ins")
                            price = price_element.text.strip()
                        except:
                            price = "0"

                        # 3. Link
                        try:
                            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except: link = ""
                        
                        # 4. Marka (İsmin ilk kelimesi genelde markadır)
                        brand = title.split(" ")[0]
                        
                        # 5. Yorum Sayısı (ratingText)
                        try:
                            rating_text = card.find_element(By.CLASS_NAME, "ratingText").text
                            rating_count = rating_text.replace("(", "").replace(")", "")
                        except: rating_count = "0"

                        # Fiyatı olmayanları alma
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
                        continue # Hatalı kartı atla
            except Exception as e:
                print(f"⚠️ Sayfa Hatası (Sayfa {page}): {e}")
                continue

    driver.quit()
    return all_products

if __name__ == "__main__":
    # 1. Verileri Çek
    data = scrape_n11_final()
    
    if len(data) > 0:
        df = pd.DataFrame(data)
        
        print("\n🧹 VERİ TEMİZLİĞİ YAPILIYOR...")
        
        # --- 1. TEMİZLİK: KOPYA ÜRÜNLERİ SİL ---
        initial_count = len(df)
        # 'Link' sütunu aynı olanları siler, ilkini tutar
        df.drop_duplicates(subset=['Link'], keep='first', inplace=True)
        final_count = len(df)
        print(f"   -> {initial_count - final_count} adet tekrar eden (reklam/kopya) ürün silindi.")
        
        # --- 2. TEMİZLİK: FİYAT FORMATI ---
        try:
            # "25.499,00 TL" -> 25499.00 (Float'a çevrilebilir format)
            df['Fiyat'] = df['Fiyat'].str.replace(" TL", "").str.replace("TL", "").str.strip()
            df['Fiyat'] = df['Fiyat'].str.replace(".", "") # Binlik ayracını sil
            df['Fiyat'] = df['Fiyat'].str.replace(",", ".") # Kuruş ayracını nokta yap
        except: 
            pass

        # Dosyayı Kaydet
        df.to_csv("tum_urunler.csv", index=False)
        try: df.to_excel("tum_urunler.xlsx", index=False)
        except: pass
        
        print("\n" + "="*50)
        print(f"✅ GÖREV TAMAMLANDI! Toplam {len(df)} EŞSİZ ve TEMİZ ürün kaydedildi.")
        print("="*50)
        print("Kategori Dağılımı:")
        print(df.groupby("Kategori").count()) 
    else:
        print("❌ Hiç veri çekilemedi. İnternet bağlantınızı kontrol edin.")