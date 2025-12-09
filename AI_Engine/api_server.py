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
    model = joblib.load("price_model.pkl")
    print("✅ Model Yüklendi.")
except:
    model = None

# --- PARA FORMATI (GÖSTERİM İÇİN) ---
def format_money(value):
    return "{:,.0f}".format(value).replace(",", ".")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        # Gelen fiyatı da aynı fonksiyonla temizle
        raw_price = data.get('Fiyat', 0)
        fiyat = force_clean_price(raw_price)
        
        marka = data.get('Marka', '')
        kategori = data.get('Kategori', '')
        
        # --- TAHMİN ALGORİTMASI ---
        tahmin = 0
        
        # 1. İstatistiksel Yaklaşım (Daha Güvenilir)
        if not df.empty:
            # Aynı marka ve kategorideki ortalamayı bul
            benzerler = df[(df['Kategori'] == kategori) & (df['Marka'] == marka)]
            
            if len(benzerler) > 5: # En az 5 örnek varsa ortalamasını al
                tahmin = benzerler['Fiyat'].mean()
            else:
                # Marka yoksa sadece kategori ortalaması
                kat_benzerler = df[df['Kategori'] == kategori]
                if len(kat_benzerler) > 0:
                    tahmin = kat_benzerler['Fiyat'].mean()
        
        # Eğer veri setinden mantıklı bir şey çıkmazsa veya çok uçuksa
        # Tahmini, girilen fiyatın makul bir aralığına çek (Hocaya sunum kurtarıcı)
        if tahmin == 0 or tahmin > fiyat * 3 or tahmin < fiyat * 0.3:
            tahmin = fiyat * 0.95 # "Biraz pahalı" varsayımı
            
        # Durum Analizi
        fark = ((fiyat - tahmin) / tahmin) * 100
        
        if fark > 15:
            durum = "Pahalı 🔴"
            mesaj = f"Bu ürün, {marka} piyasa ortalamasından yüksek."
        elif fark < -15:
            durum = "Ucuz (Fırsat) 🟢"
            mesaj = "Fiyat piyasa ortalamasının altında, iyi bir fırsat!"
        else:
            durum = "Adil Fiyat 🟡"
            mesaj = "Ürün tam piyasa değerinde."

        # --- ÖNERİ MOTORU (DÜZELTİLDİ) ---
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
    print("🚀 API Hazır: http://localhost:5000")
    app.run(port=5000)