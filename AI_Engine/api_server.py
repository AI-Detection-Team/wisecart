from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# --- FİYAT TEMİZLEME MOTORU (ZORLAMALI) ---
def force_clean_price(value):
    """
    Gelen veriyi ne olursa olsun doğru Float'a çevirir.
    Örn: "29.496,50" -> 29496.5
    Örn: "1.595" -> 1595.0
    """
    if pd.isna(value): return 0.0
    s = str(value).strip().replace("TL", "").replace(" ", "")
    
    # 1. Eğer zaten düzgün sayıysa (29496)
    if s.isdigit(): return float(s)
    
    # 2. Eğer "29.496,50" formatıysa (Türkçe)
    if "." in s and "," in s:
        s = s.replace(".", "")  # Binlik noktasını at
        s = s.replace(",", ".") # Kuruş virgülünü nokta yap
    
    # 3. Eğer sadece nokta varsa (29.496) -> Genelde binliktir
    elif "." in s:
        parts = s.split(".")
        # Eğer noktadan sonra 3 hane varsa (1.500) kesin binliktir, sil.
        if len(parts[-1]) == 3:
            s = s.replace(".", "")
        else:
            # (10.5) gibiyse ondalıktır, dokunma.
            pass
            
    # 4. Eğer sadece virgül varsa (29496,50) -> Nokta yap
    elif "," in s:
        s = s.replace(",", ".")
        
    try:
        return float(s)
    except:
        return 0.0

# --- VERİ YÜKLEME ---
df = pd.DataFrame()
try:
    df = pd.read_csv("tum_urunler_v3.csv")
    # Veri setindeki fiyatları hemen düzeltelim
    df['Fiyat'] = df['Fiyat'].apply(force_clean_price)
    # Hatalı (0 veya çok küçük) fiyatları analizden çıkar
    df = df[df['Fiyat'] > 50] 
    print(f"✅ Veri Seti Yüklendi ve Temizlendi: {len(df)} ürün.")
    print(f"📊 Veri Seti Ortalama Fiyat: {df['Fiyat'].mean():.2f} TL (Kontrol Et!)")
except Exception as e:
    print(f"❌ Veri Hatası: {e}")

# Modeli Yükle
try:
    # Bu model artık bir Pipeline (İçinde TF-IDF + Regressor var)
    model = joblib.load("price_model.pkl")
    print("✅ Şampiyon Model Yüklendi.")
except:
    model = None

# Veri setini yükle (Öneriler için)
try:
    df = pd.read_csv("tum_urunler_v3.csv")
    # Fiyatı sayıya çevir
    df['Fiyat'] = df['Fiyat'].astype(str).str.replace("TL","").str.replace(".","").str.replace(",",".")
    df['Fiyat'] = pd.to_numeric(df['Fiyat'], errors='coerce')
    print(f"✅ Veri Seti Hazır: {len(df)} ürün.")
except:
    df = pd.DataFrame()

# Para Formatı
def format_money(value):
    try: return "{:,.0f}".format(value).replace(",", ".")
    except: return str(value)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        # Gelen veriler
        fiyat = float(data.get('Fiyat', 0))
        marka = data.get('Marka', '')
        kategori = data.get('Kategori', '')
        urun_adi = data.get('Model', '') # YENİ: Ürün ismini de alıyoruz

        # --- A. YAPAY ZEKA TAHMİNİ ---
        tahmin = 0
        if model:
            try:
                # Modelin beklediği formatta DataFrame oluştur
                # Sütun isimleri eğitimdekiyle (train_model.py) AYNI olmalı
                input_df = pd.DataFrame([{
                    'Model': urun_adi, 
                    'Marka': marka, 
                    'Kategori': kategori
                }])
                
                # Pipeline her şeyi (Encoding, TF-IDF) kendi halleder
                tahmin = model.predict(input_df)[0]
            except Exception as e:
                print(f"Model Hatası: {e}")
                tahmin = 0 # Model çalışmazsa istatistiğe düş

        # --- B. İSTATİSTİK YEDEĞİ (Model Hata Verirse) ---
        if tahmin == 0:
            if not df.empty:
                benzerler = df[(df['Kategori'] == kategori) & (df['Marka'] == marka)]
                if len(benzerler) > 0: tahmin = benzerler['Fiyat'].mean()
                else: tahmin = fiyat
            else:
                tahmin = fiyat

        # --- C. DURUM ANALİZİ ---
        fark_yuzdesi = ((fiyat - tahmin) / tahmin) * 100
        tahmin_str = format_money(tahmin)
        
        if fark_yuzdesi > 15:
            durum = "Pahalı 🔴"
            mesaj = f"Yapay Zeka analizine göre bu ürün, özelliklerine kıyasla %{int(fark_yuzdesi)} daha pahalı."
        elif fark_yuzdesi < -15:
            durum = "Ucuz (Fırsat) 🟢"
            mesaj = f"Bu ürün piyasa değerinin %{int(abs(fark_yuzdesi))} altında! Fırsat olabilir."
        else:
            durum = "Adil Fiyat 🟡"
            mesaj = "Fiyat, ürünün özelliklerine ve piyasa koşullarına uygun."

        # --- D. ÖNERİLER ---
        oneriler = []
        if not df.empty:
            # Mantık: Aynı kategori, Fiyatı asıl üründen DÜŞÜK ama çok da ölü olmayan (%40 - %100 arası)
            alt_sinir = fiyat * 0.4
            ust_sinir = fiyat * 0.95 # Kendisinden ucuz olsun
            
            alternatifler = df[
                (df['Kategori'] == kategori) & 
                (df['Fiyat'] >= alt_sinir) & 
                (df['Fiyat'] <= ust_sinir)
            ].sort_values(by='Fiyat', ascending=False).head(3)
            
            for _, row in alternatifler.iterrows():
                img = row.get('Resim', '')
                if pd.isna(img) or str(img) == "nan" or img == "": 
                    img = "https://via.placeholder.com/150?text=Resim+Yok"
                
                oneriler.append({
                    "ad": row['Model'],
                    "fiyat": format_money(row['Fiyat']), 
                    "link": row['Link'],
                    "resim": img
                })

        return jsonify({
            "tahmin": format_money(tahmin),
            "durum": durum,
            "mesaj": mesaj,
            "oneriler": oneriler
        })

    except Exception as e:
        print(f"Hata: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Akıllı API (v2) Başladı...")
    app.run(port=5000)