from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
# Tüm kaynaklardan gelen isteklere izin ver - CORS ayarları
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
     }},
     supports_credentials=True)

print("🔥 API Sunucusu (Final Sürüm) Başlatılıyor...")

# 1. Modeli Yükle
model = None
try:
    model = joblib.load("price_model.pkl")
    print("✅ Model Yüklendi.")
except:
    print("⚠️ Model Yok, İstatistik Modu Aktif.")

# --- KRİTİK TEMİZLİK FONKSİYONU ---
def ultra_clean_price(price):
    if pd.isna(price): return None
    s = str(price).strip().replace("TL", "").replace(" ", "")
    
    # Türkiye standardı: 1.250,50 -> 1250.50
    if "," in s:
        s = s.replace(".", "")  # Binlik noktasını at
        s = s.replace(",", ".") # Virgülü nokta yap
    else:
        # Sadece nokta varsa (10.500 gibi) -> Noktayı sil
        if len(s.split(".")[-1]) == 3: 
            s = s.replace(".", "")
            
    try:
        val = float(s)
        # Mantık Filtresi: 100 TL altı ve 200.000 TL üstü (Tv/Monitor için) hatalıdır, at.
        if val < 100 or val > 200000: return None 
        return val
    except: return None
# ----------------------------------

# 2. Veri Setini Yükle ve TEMİZLE
df = pd.DataFrame()
try:
    df = pd.read_csv("tum_urunler_v3.csv")
    
    # Temizliği Uygula
    df['Fiyat'] = df['Fiyat'].apply(ultra_clean_price)
    
    # Bozuk verileri (None olanları) tablodan sil
    df.dropna(subset=['Fiyat', 'Model', 'Marka', 'Kategori'], inplace=True)
    
    print(f"✅ Temizlenmiş Veri Seti Hazır: {len(df)} ürün kaldı.")
    print(f"📊 Ortalama Referans Fiyat: {df['Fiyat'].mean():.2f} TL")
except Exception as e:
    print(f"❌ Veri Seti Hatası: {e}")

def format_money(value):
    return "{:,.0f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    try:
        data = request.json
        print(f"\n📩 ANALİZ İSTEĞİ: {data.get('Model')}")

        gelen_fiyat = float(data.get('Fiyat', 0))
        marka = data.get('Marka', '')
        kategori = data.get('Kategori', '')
        urun_adi = data.get('Model', '')

        # --- A. YAPAY ZEKA TAHMİNİ ---
        tahmin = 0
        kaynak = "Yapay Zeka"
        
        if model:
            try:
                input_df = pd.DataFrame([{'Model': urun_adi, 'Marka': marka, 'Kategori': kategori}])
                tahmin = model.predict(input_df)[0]
                print(f"🤖 AI Tahmini: {tahmin:.2f} TL")
            except: 
                print("⚠️ AI Tahmin Yapamadı.")

        # --- B. İSTATİSTİK YEDEĞİ (AI Saçmalarsa) ---
        # Kategorinin ortalamasını bul
        ortalama_fiyat = gelen_fiyat
        if not df.empty:
            # Önce Marka+Kategori bazlı bak
            benzerler = df[(df['Kategori'] == kategori) & (df['Marka'] == marka)]
            
            # Eğer o markadan az ürün varsa, sadece Kategoriye bak
            if len(benzerler) < 3:
                benzerler = df[df['Kategori'] == kategori]
            
            if not benzerler.empty:
                ortalama_fiyat = benzerler['Fiyat'].mean()
                print(f"📊 Pazar Ortalaması: {ortalama_fiyat:.2f} TL")

        # Mantık Kontrolü: AI, pazar ortalamasından çok sapmışsa (2 katı gibi), AI'yı yoksay
        if tahmin > (ortalama_fiyat * 2) or tahmin < (ortalama_fiyat / 3) or tahmin == 0:
            print(f"⚠️ Model aşırı uçuk tahmin yaptı ({tahmin:.0f}). Ortalamayı kullanıyorum.")
            tahmin = ortalama_fiyat
            kaynak = "Pazar Ortalaması"

        # --- C. DURUM BELİRLEME ---
        fark_yuzdesi = ((gelen_fiyat - tahmin) / tahmin) * 100
        
        if fark_yuzdesi > 15: 
            durum = "Pahalı 🔴"
            mesaj = f"{kaynak} analizine göre bu ürün piyasa ortalamasından %{int(fark_yuzdesi)} daha yüksek fiyatlı."
        elif fark_yuzdesi < -15:
            durum = "Ucuz (Fırsat) 🟢"
            mesaj = f"Bu ürün, {kategori} kategorisindeki benzerlerine göre %{int(abs(fark_yuzdesi))} daha uygun!"
        else:
            durum = "Adil Fiyat 🟡"
            mesaj = f"Fiyat, {marka} markasının piyasa standartlarına uygun."

        # --- D. ÖNERİLER (DAHA UCUZ OLANLAR) ---
        oneriler = []
        if not df.empty:
            # Aynı kategoride, şu anki fiyattan UCUZ olanları bul
            alternatifler = df[
                (df['Kategori'] == kategori) & 
                (df['Fiyat'] < gelen_fiyat) &      # Daha ucuz
                (df['Fiyat'] > gelen_fiyat * 0.4)  # Ama %40'ından da ucuz olmasın (çöp olmasın)
            ].sort_values(by='Fiyat').head(3)

            for _, row in alternatifler.iterrows():
                # Resim yoksa placeholder koy
                img = row.get('Resim', '')
                if pd.isna(img) or str(img).strip() == "" or "http" not in str(img):
                    img = "https://via.placeholder.com/60?text=Urun"
                
                oneriler.append({
                    "ad": str(row['Model']),
                    "fiyat": format_money(row['Fiyat']),
                    "link": str(row['Link']),
                    "resim": img
                })

        response = jsonify({
            "tahmin": format_money(tahmin),
            "durum": durum,
            "mesaj": mesaj,
            "oneriler": oneriler
        })
        # CORS header'larını ekle
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response

    except Exception as e:
        print(f"❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({"error": str(e)})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response, 500

def _build_cors_preflight_response():
    response = jsonify({})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add("Access-Control-Max-Age", "3600")
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)